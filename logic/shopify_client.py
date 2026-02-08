"""
Shopify GraphQL API Client für VinylLocal AI.
OAuth + GraphQL (API 2026-01). Token-Tausch per REST.
Bilder: stagedUploadsCreate → HTTP PUT → productCreateMedia.
"""

import hashlib
import logging
import hmac
import html
import json
import mimetypes
import re
import requests
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode

from core.tracklist import html_to_tracklist_text

# API-Version für Shopify Admin GraphQL
API_VERSION = "2026-01"
GRAPHQL_ENDPOINT = f"/admin/api/{API_VERSION}/graphql.json"

SHOPIFY_OAUTH_SCOPES = "write_products,read_products,write_inventory,read_inventory,write_files,read_orders,read_publications,write_publications"

_log = logging.getLogger(__name__)


def _normalize_trailing_parens(s: str) -> str:
    """Entfernt überzählige schließende Klammern am Ende (z. B. '…Wood))' -> '…Wood)')."""
    if not s:
        return s
    return re.sub(r"\)+$", ")", s.strip())


def normalize_shopify_store_url(url: str) -> str:
    """
    Bereinigt die Store-URL zu reinem Host (z.B. plattenladen-2.myshopify.com).
    Entfernt https://, http:// und Schrägstriche am Ende bzw. Pfad.
    """
    if not url or not url.strip():
        return ""
    cleaned = url.strip().lower()
    if cleaned.startswith("https://"):
        cleaned = cleaned[8:].strip()
    elif cleaned.startswith("http://"):
        cleaned = cleaned[7:].strip()
    if "/" in cleaned:
        cleaned = cleaned.split("/")[0]
    return cleaned.rstrip("/")


def validate_shopify_store_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Prüft ob die Store-URL das Format name.myshopify.com hat.
    
    Args:
        url: Store-URL (z.B. "mein-shop.myshopify.com" oder "https://mein-shop.myshopify.com")
    
    Returns:
        (valid: bool, error_message: Optional[str])
    """
    if not url or not url.strip():
        return False, "Store-URL darf nicht leer sein."
    cleaned = normalize_shopify_store_url(url)
    if not cleaned:
        return False, "Store-URL darf nicht leer sein."
    pattern = r"^[a-zA-Z0-9][a-zA-Z0-9\-]*\.myshopify\.com$"
    if not re.match(pattern, cleaned):
        return False, "Ungültige Store-URL. Format: name.myshopify.com"
    return True, None


def verify_shopify_hmac(query_params: Dict[str, str], client_secret: str) -> bool:
    """
    Prüft den HMAC von Shopify OAuth Callback-Parametern.
    Shopify sendet alle Parameter außer hmac, sortiert nach Key, als message.
    """
    if not query_params or "hmac" not in query_params:
        return False
    received_hmac = query_params.get("hmac", "")
    # Build message from all params except hmac, sorted by key
    rest = {k: v for k, v in query_params.items() if k != "hmac"}
    pairs = [f"{k}={v}" for k, v in sorted(rest.items())]
    message = "&".join(pairs)
    expected = hmac.new(
        client_secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, received_hmac)


def get_shopify_install_url(
    store_url: str,
    redirect_uri: str,
    client_id: str,
    state: Optional[str] = None,
) -> str:
    """
    Erzeugt die URL zum OAuth-Start (Redirect zur Shopify-Installationsseite).
    
    Args:
        store_url: Bereinigte Store-URL (z.B. mein-shop.myshopify.com)
        redirect_uri: App-URL, an die Shopify zurückleitet (APP_URL)
        client_id: Shopify App Client ID
        state: Optionaler CSRF-State
    
    Returns:
        Vollständige authorize-URL
    """
    shop = normalize_shopify_store_url(store_url) or store_url
    params = {
        "client_id": client_id,
        "scope": SHOPIFY_OAUTH_SCOPES,
        "redirect_uri": redirect_uri,
    }
    if state:
        params["state"] = state
    return f"https://{shop}/admin/oauth/authorize?{urlencode(params)}"


def exchange_code_for_token(
    shop: str,
    code: str,
    client_id: str,
    client_secret: str,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Tauscht den OAuth-Code gegen einen Access Token (REST).
    
    Returns:
        (access_token, error_message) – bei Erfolg error_message=None
    """
    shop = normalize_shopify_store_url(shop)
    if not shop:
        return None, "Ungültige Shop-URL."
    url = f"https://{shop}/admin/oauth/access_token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
    }
    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        token = (data.get("access_token") or "").strip()
        if not token:
            return None, "Kein access_token in der Antwort."
        return token, None
    except requests.exceptions.RequestException as e:
        msg = str(e)
        if hasattr(e, "response") and e.response is not None:
            try:
                err = e.response.json()
                if isinstance(err, dict) and "error" in err:
                    msg = err.get("error_description", err.get("error", msg))
            except Exception:
                msg = (e.response.text or msg)[:300]
        return None, msg


class ShopifyClient:
    """GraphQL Client für die Shopify Admin API."""
    
    def __init__(self, store_url: str, access_token: str):
        """
        Initialisiert den Shopify GraphQL Client.
        
        Args:
            store_url: Store-URL (z.B. "mein-shop.myshopify.com", ohne https://)
            access_token: Admin API Access Token
        """
        self.store_url = normalize_shopify_store_url(store_url) or store_url.strip().lower().split("/")[0]
        self.access_token = access_token
        self.graphql_url = f"https://{self.store_url}{GRAPHQL_ENDPOINT}"
        self.headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.access_token,
        }
    
    def execute_query(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Führt eine GraphQL-Anfrage aus.
        
        Args:
            query: GraphQL-Query oder Mutation
            variables: Optionale Variablen für die Query
        
        Returns:
            Parsed JSON-Response
        
        Raises:
            RuntimeError: Bei HTTP-Fehlern oder GraphQL errors
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        try:
            response = requests.post(
                self.graphql_url,
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            
            # GraphQL-Level Fehler prüfen (errors kann Liste oder einzelner String sein)
            if "errors" in data and data["errors"]:
                raw = data["errors"]
                err_list = [raw] if isinstance(raw, str) else raw
                messages = []
                for e in err_list:
                    if isinstance(e, dict):
                        messages.append(e.get("message", str(e)))
                    else:
                        messages.append(str(e))
                raise RuntimeError("; ".join(messages))
            
            return data
        except requests.exceptions.RequestException as e:
            if hasattr(e, "response") and e.response is not None:
                try:
                    err_body = e.response.json()
                    if "errors" in err_body:
                        raw = err_body["errors"]
                        err_list = [raw] if isinstance(raw, str) else raw
                        msgs = []
                        for x in err_list:
                            msgs.append(x.get("message", str(x)) if isinstance(x, dict) else str(x))
                        raise RuntimeError("; ".join(msgs)) from e
                except (ValueError, KeyError):
                    pass
                raise RuntimeError(f"HTTP {e.response.status_code}: {e.response.text[:200]}") from e
            raise RuntimeError(str(e)) from e
    
    def _extract_user_errors(self, data: Dict[str, Any], mutation_key: str) -> Optional[str]:
        """Extrahiert userErrors aus einer Mutation-Response."""
        mut_data = data.get("data", {}).get(mutation_key)
        if not mut_data:
            return None
        errors = mut_data.get("userErrors", [])
        if not errors:
            return None
        return "; ".join(
            e.get("message", str(e)) if isinstance(e, dict) else str(e)
            for e in errors
        )
    
    def _upload_image_to_staged(self, file_path: str, mime_type: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Staged-Upload für ein Bild: stagedUploadsCreate → PUT zur url mit parameters als Headers.
        
        Args:
            file_path: Absoluter Pfad zur Bilddatei.
            mime_type: Optional; sonst aus Dateiendung (mimetypes.guess_type), Fallback image/jpeg.
        
        Returns:
            (resource_url, error_message) – bei Erfolg error_message=None.
        """
        path = Path(file_path)
        if not path.is_file():
            return None, f"Datei nicht gefunden: {file_path}"
        filename = path.name
        guessed, _ = mimetypes.guess_type(str(path))
        mime = mime_type or guessed or "image/jpeg"
        staged_mutation = """
        mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
            stagedUploadsCreate(input: $input) {
                stagedTargets {
                    url
                    resourceUrl
                    parameters { name value }
                }
                userErrors { field message }
            }
        }
        """
        variables = {
            "input": [
                {
                    "resource": "IMAGE",
                    "filename": filename,
                    "mimeType": mime,
                }
            ]
        }
        try:
            data = self.execute_query(staged_mutation, variables)
        except RuntimeError as e:
            return None, str(e)
        err = self._extract_user_errors(data, "stagedUploadsCreate")
        if err:
            return None, err
        targets = (data.get("data") or {}).get("stagedUploadsCreate", {}).get("stagedTargets", [])
        if not targets:
            return None, "Kein Staged-Target von Shopify erhalten."
        target = targets[0]
        url = target.get("url")
        resource_url = target.get("resourceUrl")
        params = target.get("parameters") or []
        if not url or not resource_url:
            return None, "Staged-Target ohne url oder resourceUrl."
        headers = {p.get("name"): p.get("value") for p in params if p.get("name") is not None}
        try:
            with open(path, "rb") as f:
                body = f.read()
        except OSError as e:
            return None, f"Datei lesen fehlgeschlagen: {e}"
        try:
            put_resp = requests.put(url, data=body, headers=headers, timeout=60)
        except requests.exceptions.RequestException as e:
            return None, f"PUT-Upload fehlgeschlagen: {e}"
        if not (200 <= put_resp.status_code < 300):
            msg = put_resp.text[:300] if put_resp.text else ""
            return None, f"PUT-Upload {put_resp.status_code}: {msg}"
        return resource_url, None
    
    def add_product_media(self, product_id: str, media: List[Dict[str, Any]]) -> Optional[str]:
        """
        Hängt Medien an ein Produkt (productCreateMedia). originalSource = resourceUrl aus Staged-Upload.
        
        Args:
            product_id: Shopify Product GID.
            media: Liste von { "originalSource": resourceUrl, "mediaContentType": "IMAGE", "alt": optional }.
        
        Returns:
            None bei Erfolg, sonst Fehlermeldung.
        """
        if not media:
            return None
        mutation = """
        mutation productCreateMedia($productId: ID!, $media: [CreateMediaInput!]!) {
            productCreateMedia(productId: $productId, media: $media) {
                media { id }
                mediaUserErrors { field message }
                userErrors { field message }
            }
        }
        """
        variables = {"productId": product_id, "media": media}
        try:
            data = self.execute_query(mutation, variables)
        except RuntimeError as e:
            return str(e)
        payload = (data.get("data") or {}).get("productCreateMedia", {})
        media_errors = payload.get("mediaUserErrors") or []
        user_errors = payload.get("userErrors") or []
        all_errors = media_errors + user_errors
        if all_errors:
            return "; ".join(
                e.get("message", str(e)) if isinstance(e, dict) else str(e)
                for e in all_errors
            )
        return None
    
    def get_orders_sales_totals(
        self, query_filter: Optional[str] = None
    ) -> Tuple[int, float, Optional[str]]:
        """
        Aggregiert Menge und Umsatz aus bezahlten Shopify-Orders (GraphQL, paginiert).
        Benötigt read_orders. Nur Orders der letzten 60 Tage (Shopify-Standard ohne read_all_orders).

        Args:
            query_filter: Optionaler Query-String (z.B. "financial_status:paid").
                          Default: nur bezahlte Orders.

        Returns:
            (total_quantity, total_revenue, error_message)
            - Bei Erfolg: error_message ist None.
            - Bei API-/Scope-Fehler: (0, 0.0, "Fehlermeldung").
        """
        query_str = (query_filter or "financial_status:paid").strip()
        orders_query = """
        query ordersSalesTotals($query: String, $first: Int!, $after: String) {
            orders(first: $first, query: $query, after: $after) {
                edges {
                    node {
                        totalPriceSet {
                            shopMoney { amount }
                        }
                        lineItems(first: 100) {
                            edges {
                                node { quantity }
                            }
                        }
                    }
                }
                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }
        """
        total_quantity = 0
        total_revenue = 0.0
        cursor: Optional[str] = None
        try:
            while True:
                variables: Dict[str, Any] = {"first": 250}
                if query_str:
                    variables["query"] = query_str
                if cursor:
                    variables["after"] = cursor
                data = self.execute_query(orders_query, variables)
                orders_data = (data.get("data") or {}).get("orders")
                if not isinstance(orders_data, dict):
                    return (0, 0.0, "Ungültige API-Antwort (orders).")
                edges = orders_data.get("edges") or []
                for edge in edges:
                    node = edge.get("node") if isinstance(edge, dict) else None
                    if not isinstance(node, dict):
                        continue
                    # Umsatz: totalPriceSet.shopMoney.amount (String)
                    price_set = node.get("totalPriceSet")
                    if isinstance(price_set, dict):
                        shop_money = price_set.get("shopMoney")
                        if isinstance(shop_money, dict):
                            amount_str = shop_money.get("amount")
                            if amount_str is not None:
                                try:
                                    total_revenue += float(amount_str)
                                except (TypeError, ValueError):
                                    pass
                    # Menge: Summe lineItems.quantity
                    line_items = node.get("lineItems") or {}
                    li_edges = (line_items.get("edges") or []) if isinstance(line_items, dict) else []
                    for li_edge in li_edges:
                        li_node = li_edge.get("node") if isinstance(li_edge, dict) else None
                        if isinstance(li_node, dict):
                            try:
                                total_quantity += int(li_node.get("quantity") or 0)
                            except (TypeError, ValueError):
                                pass
                page_info = orders_data.get("pageInfo") or {}
                if not isinstance(page_info, dict) or not page_info.get("hasNextPage"):
                    break
                cursor = page_info.get("endCursor")
                if not cursor:
                    break
            return (total_quantity, total_revenue, None)
        except RuntimeError as e:
            return (0, 0.0, str(e))

    def test_connection(self) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Testet die Verbindung zum Shopify-Shop via GraphQL.
        
        Returns:
            (success, error_message, shop_info)
        """
        query = """
        {
            shop {
                name
                configCanDesignOwnCart
                plan { publicDisplayName }
            }
        }
        """
        try:
            data = self.execute_query(query)
            inner = data.get("data")
            if not isinstance(inner, dict):
                return False, "Ungültige API-Antwort (data ist kein Objekt).", None
            shop = inner.get("shop")
            if not isinstance(shop, dict):
                err = self._extract_user_errors(data, "shop") or "Shop-Daten nicht erhalten."
                return False, err, None
            return True, None, shop
        except RuntimeError as e:
            return False, str(e), None
    
    def ensure_vinyl_metafield_definitions(self) -> Optional[str]:
        """
        Legt die Metafeld-Definitionen für Vinyl-Produkte an (vinyl.artist, vinyl.label,
        vinyl.condition, vinyl.catalog_number). Ignoriert bereits existierende Definitionen.
        
        Returns:
            None bei Erfolg, sonst Fehlermeldung.
        """
        definitions = [
            ("Artist", "vinyl", "artist", "single_line_text_field"),
            ("Label", "vinyl", "label", "single_line_text_field"),
            ("Condition", "vinyl", "condition", "single_line_text_field"),
            ("Catalog number", "vinyl", "catalog_number", "single_line_text_field"),
            ("Product category", "vinyl", "product_category", "single_line_text_field"),
        ]
        mutation = """
        mutation metafieldDefinitionCreate($definition: MetafieldDefinitionInput!) {
            metafieldDefinitionCreate(definition: $definition) {
                createdDefinition { id name }
                userErrors { field message code }
            }
        }
        """
        for name, namespace, key, type_name in definitions:
            variables = {
                "definition": {
                    "name": name,
                    "namespace": namespace,
                    "key": key,
                    "type": type_name,
                    "ownerType": "PRODUCT",
                }
            }
            try:
                data = self.execute_query(mutation, variables)
            except RuntimeError as e:
                return str(e)
            err = self._extract_user_errors(data, "metafieldDefinitionCreate")
            if err and "already exists" not in err.lower() and "duplicate" not in err.lower():
                return err
        return None
    
    def _tracklist_to_html(self, tracklist_raw: Any) -> str:
        """Konvertiert Trackliste (JSON oder Text) in HTML."""
        if not tracklist_raw:
            return ""
        try:
            if isinstance(tracklist_raw, str):
                # Versuche JSON zu parsen (Tabellenformat)
                try:
                    table = json.loads(tracklist_raw)
                except json.JSONDecodeError:
                    table = None
                if table is None or not isinstance(table, list):
                    # Als lesbaren Text verwenden (nummerierte Liste, kein Bullet)
                    lines = tracklist_raw.strip().split("\n")
                    items = [f"<li>{html.escape(line)}</li>" for line in lines if line.strip()]
                    return f"<ol>{''.join(items)}</ol>" if items else ""
            else:
                table = tracklist_raw if isinstance(tracklist_raw, list) else []
            
            if not table:
                return ""
            items = []
            for track in table:
                if isinstance(track, dict):
                    title = track.get("Titel", track.get("title", ""))
                    length = track.get("Länge", track.get("length", ""))
                    line = str(title) if title else ""
                    if length:
                        line += f" ({length})" if line else length
                else:
                    line = str(track)
                if line:
                    items.append(f"<li>{html.escape(line)}</li>")
            return f"<ol>{''.join(items)}</ol>" if items else ""
        except Exception:
            return ""

    def _tracklist_to_html_grouped(self, tracklist_raw: Any) -> str:
        """
        Konvertiert Trackliste in HTML, gruppiert nach Seite.
        Einheitlich Zahlen: "Seite 1:", "Seite 2:", "Seite 3:", …
        """
        if not tracklist_raw:
            return ""
        try:
            if isinstance(tracklist_raw, str):
                try:
                    table = json.loads(tracklist_raw)
                except json.JSONDecodeError:
                    table = None
                if table is None or not isinstance(table, list):
                    return self._tracklist_to_html(tracklist_raw)
            else:
                table = tracklist_raw if isinstance(tracklist_raw, list) else []
            if not table:
                return ""
            # Gruppieren nach Seite
            by_side: Dict[str, List[Dict[str, Any]]] = {}
            for track in table:
                if isinstance(track, dict):
                    seite = str(track.get("Seite", "")).strip() or "1"
                    if seite not in by_side:
                        by_side[seite] = []
                    by_side[seite].append(track)
                else:
                    if "_" not in by_side:
                        by_side["_"] = []
                    by_side["_"].append(track)
            # Sortierung: 1, 2, 3, ... dann Rest
            def side_key(s: str) -> tuple:
                if s == "_":
                    return (999, "_")
                try:
                    return (int(s), s)
                except ValueError:
                    return (99, s)
            parts = []
            for seite in sorted(by_side.keys(), key=side_key):
                label = f"Seite {seite}:" if seite != "_" else "Weitere:"
                parts.append(f"<p><strong>{html.escape(label)}</strong></p>")
                items = []
                for track in by_side[seite]:
                    if isinstance(track, dict):
                        title = track.get("Titel", track.get("title", ""))
                        length = track.get("Länge", track.get("length", ""))
                        line = str(title) if title else ""
                        if length:
                            line += f" ({length})" if line else length
                    else:
                        line = str(track)
                    if line:
                        items.append(f"<li>{html.escape(line)}</li>")
                if items:
                    parts.append(f"<ol>{''.join(items)}</ol>")
            return "\n".join(parts)
        except Exception:
            return self._tracklist_to_html(tracklist_raw)

    def _build_description_html(self, record_data: Dict[str, Any]) -> str:
        """
        Baut die komplette Shopify-Beschreibung: Metadaten, Titelliste (gruppiert), Zustandsbeschreibung.
        Reihenfolge: Block 1 Metadaten, Block 2 Titelliste, Block 3 Zustandsbeschreibung.
        """
        artist = (record_data.get("artist") or "").strip()
        title = (record_data.get("title") or "").strip()
        product_title = f"{artist} - {title}" if (artist or title) else "Vinyl"
        blocks = []
        # Block 1: Metadaten (Interpret, Titel, Label, Katalognummer, Jahr, Format, Genre)
        meta_labels = [
            ("artist", "Interpret:"),
            ("title", "Titel:"),
            ("label", "Label:"),
            ("cat_no", "Katalognummer:"),
            ("year", "Jahr:"),
            ("format", "Format:"),
            ("genre", "Genre:"),
        ]
        meta_parts = []
        for key, label in meta_labels:
            val = record_data.get(key)
            if key == "year" and val is not None:
                val = str(val).strip()
            else:
                val = (val or "").strip() if isinstance(val, str) else ""
            if val:
                meta_parts.append(f"<p><strong>{html.escape(label)}</strong> {html.escape(str(val))}</p>")
        if meta_parts:
            blocks.append("\n".join(meta_parts))
        # Block 2: Titelliste (gruppiert nach Seite)
        tracklist_html = self._tracklist_to_html_grouped(record_data.get("tracklist"))
        if tracklist_html:
            blocks.append("<p><strong>Titelliste:</strong></p>\n" + tracklist_html)
        # Block 3: Zustandsbeschreibung – vier konfigurierbare Absätze, danach entweder individuelle Bewertung oder allgemeiner Zustandstext (ohne "Zustand: VG")
        zustand_block_parts = []
        zustand_1 = (record_data.get("shopify_zustand_1") or "").strip()
        zustand_2 = (record_data.get("shopify_zustand_2") or "").strip()
        zustand_3 = (record_data.get("shopify_zustand_3") or "").strip()
        zustand_customer = (record_data.get("shopify_zustand_customer") or "").strip()
        for p in [zustand_1, zustand_2, zustand_3, zustand_customer]:
            if p:
                zustand_block_parts.append(f"<p>{html.escape(p)}</p>")
        individual_enabled = record_data.get("individual_condition_enabled") == 1 or record_data.get("individual_condition_enabled") is True
        if individual_enabled:
            media = (record_data.get("media_condition") or "").strip()
            sleeve = (record_data.get("sleeve_condition") or "").strip()
            if media or sleeve:
                parts_line = []
                if media:
                    parts_line.append(f"Zustand Medium: {html.escape(media)}")
                if sleeve:
                    parts_line.append(f"Zustand Cover: {html.escape(sleeve)}")
                zustand_block_parts.append(f"<p><strong>{' – '.join(parts_line)}</strong></p>")
            individual_text = (record_data.get("individual_condition_text") or "").strip()
            if individual_text:
                zustand_block_parts.append(f"<p>{html.escape(individual_text)}</p>")
        else:
            shopify_zustand_general = (record_data.get("shopify_zustand_general") or "").strip()
            if shopify_zustand_general:
                zustand_block_parts.append(f"<p>{html.escape(shopify_zustand_general)}</p>")
        shopify_zustand_after_condition = (record_data.get("shopify_zustand_after_condition") or "").strip()
        if shopify_zustand_after_condition:
            zustand_block_parts.append(f"<p>{html.escape(shopify_zustand_after_condition)}</p>")
        if zustand_block_parts:
            blocks.append("<p><strong>Zustandsbeschreibung:</strong></p>\n" + "\n".join(zustand_block_parts))
        description_html = "\n\n".join(blocks).strip()
        if not description_html:
            description_html = f"<p>Vinyl: {html.escape(product_title)}</p>"
        return description_html

    # Offizielle Shopify-Taxonomie (Shopify product-taxonomy: me_media.yml)
    # Media > Music & Sound Recordings
    TAXONOMY_MUSIC_SOUND_RECORDINGS_GID = "gid://shopify/TaxonomyCategory/me-3"
    # Media > Music & Sound Recordings > Records & LPs (Schallplatten und LPs)
    TAXONOMY_RECORDS_LPS_GID = "gid://shopify/TaxonomyCategory/me-3-4"
    # Media > Music & Sound Recordings > Vinyl (Alternative)
    TAXONOMY_VINYL_GID = "gid://shopify/TaxonomyCategory/me-3-6"
    # Standard-Kategorie-Text für Vinyl (wenn nichts gesetzt) → löst zu Records & LPs auf
    DEFAULT_VINYL_CATEGORY_NAME = "Schallplatten und LPs in Musik & Tonaufnahmen"

    def _resolve_taxonomy_category_id(self, category_name: str) -> Optional[str]:
        """
        Sucht in der Shopify-Produkt-Taxonomie nach einer Kategorie (z. B. „Schallplatten und LPs in Musik & Tonaufnahmen“)
        und gibt die TaxonomyCategory-ID zurück. Für Vinyl/LPs: bevorzugt Records & LPs (me-3-4), sonst Music & Sound Recordings (me-3).
        """
        def _valid_gid(node_id: Any) -> bool:
            if not node_id or not isinstance(node_id, str):
                return False
            return node_id.startswith("gid://shopify/TaxonomyCategory/")

        category_name = (category_name or "").strip()
        # Immer „Records & LPs“ (me-3-4) für Musik/Vinyl-Kontext → Anzeige „Schallplatten und LPs“ (nie „Vinyl“ me-3-6)
        if category_name:
            lower = category_name.lower()
            if any(k in lower for k in (
                "schallplatte", "vinyl", " lp", "lps", "platte", "records & lps",
                "musik", "tonaufnahme", "music", "sound recording", "media"
            )):
                return self.TAXONOMY_RECORDS_LPS_GID
        search_terms = [category_name, "Schallplatten und LPs", "Records & LPs", "Schallplatten", "Music Sound Recordings", "Music & Sound", "LP"]
        taxonomy_query = """
        query taxonomySearch($search: String!, $first: Int!) {
            taxonomy {
                categories(search: $search, first: $first) {
                    nodes { id fullName name isLeaf }
                    edges { node { id fullName name isLeaf } }
                }
            }
        }
        """
        for term in search_terms:
            if not term:
                continue
            try:
                data = self.execute_query(taxonomy_query, {"search": term, "first": 25})
            except RuntimeError:
                continue
            taxonomy = (data.get("data") or {}).get("taxonomy")
            if not isinstance(taxonomy, dict):
                continue
            cats = taxonomy.get("categories") or {}
            nodes = cats.get("nodes") or []
            if not nodes and cats.get("edges"):
                nodes = [e.get("node") for e in cats["edges"] if e.get("node")]
            for node in nodes:
                if not isinstance(node, dict):
                    continue
                nid = node.get("id")
                if not _valid_gid(nid):
                    continue
                full = (node.get("fullName") or "").strip()
                if full == category_name:
                    return nid
                if category_name in full or (term and term in full):
                    return nid
            if nodes:
                first_id = nodes[0].get("id") if isinstance(nodes[0], dict) else None
                if _valid_gid(first_id) and first_id != self.TAXONOMY_VINYL_GID:
                    return first_id

        # Fallback für Musik/Vinyl: zuerst globale Suche nach Vinyl/Schallplatten, nur Treffer im Zweig Media/Music
        if category_name and (
            "schallplatte" in category_name.lower() or "lp" in category_name.lower()
            or "musik" in category_name.lower() or "tonaufnahme" in category_name.lower()
            or "music" in category_name.lower() or "vinyl" in category_name.lower()
        ):
            vinyl_keywords = ("vinyl", "schallplatte", "lp", "platte")
            branch_keywords = ("music", "media", "musik", "tonaufnahme")
            for global_term in ("Vinyl", "Schallplatten", "Vinyl records", "Records and LPs"):
                try:
                    data = self.execute_query(taxonomy_query, {"search": global_term, "first": 30})
                except RuntimeError:
                    continue
                taxonomy = (data.get("data") or {}).get("taxonomy")
                if not isinstance(taxonomy, dict):
                    continue
                cats = taxonomy.get("categories") or {}
                nodes = cats.get("nodes") or []
                if not nodes and cats.get("edges"):
                    nodes = [e.get("node") for e in cats["edges"] if e.get("node")]
                for node in nodes:
                    if not isinstance(node, dict):
                        continue
                    nid = node.get("id")
                    if not _valid_gid(nid):
                        continue
                    if nid == self.TAXONOMY_VINYL_GID:
                        continue  # „Vinyl“ (me-3-6) überspringen, wir wollen „Records & LPs“ (me-3-4)
                    full = (node.get("fullName") or "").lower()
                    name = (node.get("name") or "").lower()
                    in_branch = any(b in full for b in branch_keywords)
                    has_vinyl = any(kw in full or kw in name for kw in vinyl_keywords)
                    if in_branch and has_vinyl:
                        return nid
                for node in nodes:
                    if not isinstance(node, dict):
                        continue
                    nid = node.get("id")
                    if not _valid_gid(nid) or nid == self.TAXONOMY_VINYL_GID:
                        continue
                    full = (node.get("fullName") or "").lower()
                    if any(b in full for b in branch_keywords) and ("vinyl" in full or "schallplatte" in full or "lp" in full):
                        return nid

            # Danach: Unterkategorien von me-3 (Media > Music & Sound Recordings) durchsuchen
            children_query = """
            query taxonomyChildren($parentId: ID!, $first: Int!) {
                taxonomy {
                    categories(childrenOf: $parentId, first: $first) {
                        nodes { id fullName name }
                        edges { node { id fullName name } }
                    }
                }
            }
            """
            try:
                child_data = self.execute_query(
                    children_query,
                    {"parentId": self.TAXONOMY_MUSIC_SOUND_RECORDINGS_GID, "first": 50},
                )
            except RuntimeError:
                return self.TAXONOMY_RECORDS_LPS_GID
            taxonomy = (child_data.get("data") or {}).get("taxonomy")
            if not isinstance(taxonomy, dict):
                return self.TAXONOMY_RECORDS_LPS_GID
            cats = taxonomy.get("categories") or {}
            child_nodes = cats.get("nodes") or []
            if not child_nodes and cats.get("edges"):
                child_nodes = [e.get("node") for e in cats["edges"] if e.get("node")]
            for node in child_nodes:
                if not isinstance(node, dict):
                    continue
                nid = node.get("id")
                if not _valid_gid(nid):
                    continue
                full = (node.get("fullName") or "").lower()
                name = (node.get("name") or "").lower()
                if any(kw in full or kw in name for kw in vinyl_keywords):
                    return nid
            return self.TAXONOMY_RECORDS_LPS_GID
        return None

    def _fetch_product_category(self, product_gid: str) -> None:
        """
        Liest die von Shopify gespeicherte Produktkategorie (id, fullName) und loggt sie.
        Nur für Debug: prüfen, ob gesendete Kategorie tatsächlich übernommen wurde.
        """
        if not product_gid:
            return
        query = """
        query productCategory($id: ID!) {
            product(id: $id) {
                id
                category { id fullName }
            }
        }
        """
        try:
            data = self.execute_query(query, {"id": product_gid})
            product = (data.get("data") or {}).get("product")
            if not isinstance(product, dict):
                return
            cat = product.get("category")
            if isinstance(cat, dict):
                cid = cat.get("id") or "(leer)"
                full = cat.get("fullName") or "(leer)"
                _log.info("Shopify Produktkategorie gespeichert: id=%s fullName=%s", cid, full)
            else:
                _log.info("Shopify Produktkategorie: nicht gesetzt (category=%s)", type(cat).__name__)
        except RuntimeError as e:
            _log.debug("Kategorie-Abfrage fehlgeschlagen: %s", e)

    def _find_product_by_catalog_number(self, catalog_number: str) -> Optional[str]:
        """
        Sucht ein Produkt anhand des Metafelds vinyl.catalog_number.
        Treffer werden per node(id) verifiziert: nur ACTIVE und gleiche catalog_number.
        Fail-open: Bei API-Fehlern wird None zurückgegeben (kein Duplikat angenommen).
        
        Returns:
            Produkt-GID bei verifiziertem Treffer, sonst None.
        """
        if not catalog_number or not catalog_number.strip():
            return None
        catalog_number = catalog_number.strip()
        # Query-Wert escapen: Backslash und Anführungszeichen
        escaped = catalog_number.replace("\\", "\\\\").replace('"', '\\"')
        query_str = f'status:active metafields.vinyl.catalog_number:"{escaped}"'
        products_query = """
        query productsByCatalogNumber($query: String!, $first: Int!) {
            products(first: $first, query: $query) {
                edges {
                    node { id }
                }
            }
        }
        """
        try:
            data = self.execute_query(products_query, {"query": query_str, "first": 1})
        except RuntimeError:
            return None
        edges = (data.get("data") or {}).get("products", {}).get("edges", [])
        if not edges:
            return None
        node = edges[0].get("node")
        if not isinstance(node, dict):
            return None
        product_id = node.get("id")
        if not product_id:
            return None
        # Verifizieren: node(id) abfragen, nur bei status ACTIVE und passendem Metafeld wiederverwenden
        node_query = """
        query productNode($id: ID!) {
            node(id: $id) {
                ... on Product {
                    status
                    metafield(namespace: "vinyl", key: "catalog_number") { value }
                }
            }
        }
        """
        try:
            node_data = self.execute_query(node_query, {"id": product_id})
        except RuntimeError:
            return None
        product_node = (node_data.get("data") or {}).get("node")
        if not isinstance(product_node, dict):
            return None
        if product_node.get("status") != "ACTIVE":
            return None
        mf = product_node.get("metafield")
        mf_value = (mf.get("value") if isinstance(mf, dict) else None) or ""
        if mf_value.strip() != catalog_number:
            return None
        return product_id
    
    def _get_first_location_id(self) -> Optional[str]:
        """Erste Shop-Location-ID (GID) für Inventar-Operationen. None bei Fehler."""
        query = """
        query locationsFirst($first: Int!) {
            locations(first: $first) {
                nodes { id }
            }
        }
        """
        try:
            data = self.execute_query(query, {"first": 1})
        except RuntimeError:
            return None
        nodes = (data.get("data") or {}).get("locations", {}).get("nodes", [])
        if not nodes or not isinstance(nodes[0], dict):
            return None
        return nodes[0].get("id")
    
    def _get_online_store_publication_id(self) -> Optional[str]:
        """
        Ermittelt die Publication-ID des Verkaufskanals „Online Store“.
        Auswahl: (1) catalog.title kennzeichnet Online Store, (2) supportsFuturePublishing, (3) erste Publication.
        Falls catalog/AppCatalog in der API-Version nicht verfügbar sind, greifen die Fallbacks.
        Returns:
            Publication-GID (z. B. gid://shopify/Publication/123) oder None bei Fehler.
        """
        query = """
        query publicationsFirst($first: Int!) {
            publications(first: $first) {
                nodes {
                    id
                    supportsFuturePublishing
                    catalog {
                        ... on AppCatalog {
                            title
                        }
                    }
                }
            }
        }
        """
        try:
            data = self.execute_query(query, {"first": 50})
        except RuntimeError:
            return None
        nodes = (data.get("data") or {}).get("publications", {}).get("nodes", [])
        if not nodes:
            return None

        def _catalog_title(node: dict) -> Optional[str]:
            catalog = node.get("catalog") if isinstance(node, dict) else None
            if not isinstance(catalog, dict):
                return None
            return (catalog.get("title") or "").strip() or None

        # 1. Bevorzuge Publication, deren catalog.title „Online Store“ kennzeichnet (oder Shop/Store, lokalisiert)
        online_keywords = ("online", "shop", "store", "website")
        for node in nodes:
            if not isinstance(node, dict):
                continue
            title = _catalog_title(node)
            if title and any(kw in title.lower() for kw in online_keywords):
                pub_id = node.get("id")
                if pub_id:
                    return pub_id
        # 2. Fallback: supportsFuturePublishing (typisch für Online Store)
        for node in nodes:
            if isinstance(node, dict) and node.get("supportsFuturePublishing"):
                pub_id = node.get("id")
                if pub_id:
                    return pub_id
        # 3. Fallback: erste Publication
        return nodes[0].get("id") if isinstance(nodes[0], dict) else None

    def get_online_store_publication_id(self) -> Optional[str]:
        """
        Öffentlicher Getter für die Publication-ID des Online Store (z. B. für Diagnose in den Einstellungen).
        Returns:
            Publication-GID oder None.
        """
        return self._get_online_store_publication_id()
    
    def publish_product_to_online_store(self, product_id: str) -> Optional[str]:
        """
        Veröffentlicht ein Produkt auf dem Verkaufskanal „Online Store“ (Shop sichtbar).
        Requires write_publications scope.
        Returns:
            None bei Erfolg, Fehlermeldung bei Fehler.
        """
        if not product_id or not product_id.strip():
            return "Keine Produkt-ID."
        product_gid = self._normalize_product_gid(product_id)
        if not product_gid.startswith("gid://"):
            product_gid = f"gid://shopify/Product/{product_gid}" if product_gid.isdigit() else product_id
        publication_id = self._get_online_store_publication_id()
        if not publication_id:
            return "Online-Store-Publication konnte nicht ermittelt werden."
        mutation = """
        mutation publishablePublish($id: ID!, $input: [PublicationInput!]!) {
            publishablePublish(id: $id, input: $input) {
                publishable {
                    ... on Product { id }
                }
                userErrors { field message }
            }
        }
        """
        try:
            data = self.execute_query(mutation, {
                "id": product_gid,
                "input": [{"publicationId": publication_id}],
            })
        except RuntimeError as e:
            return str(e)
        err = self._extract_user_errors(data, "publishablePublish")
        if err:
            return err
        return None
    
    def _get_variant_inventory_item_id(self, variant_id: str) -> Optional[str]:
        """InventoryItem-ID (GID) zu einer ProductVariant-ID. None bei Fehler."""
        query = """
        query variantInventoryItem($id: ID!) {
            node(id: $id) {
                ... on ProductVariant {
                    inventoryItem { id }
                }
            }
        }
        """
        try:
            data = self.execute_query(query, {"id": variant_id})
        except RuntimeError:
            return None
        node = (data.get("data") or {}).get("node")
        if not isinstance(node, dict):
            return None
        inv = node.get("inventoryItem")
        if not isinstance(inv, dict):
            return None
        return inv.get("id")
    
    def set_inventory_quantity(self, variant_id: str, quantity: int) -> Optional[str]:
        """
        Setzt die verfügbare Menge für eine Variante an der ersten Location.
        Returns: None bei Erfolg, Fehlermeldung bei Fehler.
        """
        location_id = self._get_first_location_id()
        if not location_id:
            return "Keine Location gefunden (Shop muss mindestens eine Location haben)."
        inventory_item_id = self._get_variant_inventory_item_id(variant_id)
        if not inventory_item_id:
            return "InventoryItem für Variante nicht gefunden."
        mutation = """
        mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
            inventorySetQuantities(input: $input) {
                inventoryAdjustmentGroup { reason }
                userErrors { field message }
            }
        }
        """
        variables = {
            "input": {
                "name": "available",
                "reason": "correction",
                "ignoreCompareQuantity": True,
                "quantities": [
                    {
                        "inventoryItemId": inventory_item_id,
                        "locationId": location_id,
                        "quantity": max(0, quantity),
                    }
                ],
            }
        }
        try:
            data = self.execute_query(mutation, variables)
        except RuntimeError as e:
            return str(e)
        err = self._extract_user_errors(data, "inventorySetQuantities")
        if err:
            return err
        return None
    
    def _normalize_product_gid(self, shopify_product_id: str) -> str:
        """Stellt sicher, dass die Produkt-ID im Format gid://shopify/Product/123 vorliegt."""
        raw = (shopify_product_id or "").strip()
        if not raw:
            return ""
        if raw.startswith("gid://"):
            return raw
        # Nur Ziffern/ID am Ende verwenden (falls versehentlich URL oder Pfad gespeichert)
        numeric_part = raw.split("/")[-1].split("?")[0]
        if numeric_part.isdigit():
            return f"gid://shopify/Product/{numeric_part}"
        return raw

    def _get_variant_id_for_product(self, shopify_product_id: str) -> Optional[str]:
        """Erste Varianten-ID (GID) zu einer Produkt-GID. None bei Fehler."""
        gid = self._normalize_product_gid(shopify_product_id)
        if not gid:
            return None
        query = """
        query productVariantId($id: ID!) {
            node(id: $id) {
                ... on Product {
                    variants(first: 1) {
                        nodes { id }
                    }
                }
            }
        }
        """
        try:
            data = self.execute_query(query, {"id": gid})
        except RuntimeError:
            return None
        node = (data.get("data") or {}).get("node")
        if not isinstance(node, dict):
            return None
        nodes = node.get("variants", {}).get("nodes", [])
        if not nodes or not isinstance(nodes[0], dict):
            return None
        return nodes[0].get("id")

    def set_inventory_quantity_for_product(self, shopify_product_id: str, quantity: int) -> Optional[str]:
        """
        Setzt die verfügbare Menge für ein Produkt in Shopify (erste Variante, erste Location).
        Returns: None bei Erfolg, Fehlermeldung bei Fehler.
        """
        variant_id = self._get_variant_id_for_product(shopify_product_id)
        if not variant_id:
            return "Produkt oder Variante in Shopify nicht gefunden."
        return self.set_inventory_quantity(variant_id, max(0, quantity))

    def update_vinyl_product(self, shopify_product_id: str, record_data: Dict[str, Any]) -> Optional[str]:
        """
        Aktualisiert ein bestehendes Vinyl-Produkt in Shopify: Titel, Beschreibung,
        Vendor, Metafields (artist, label, condition, catalog_number) und Varianten-Preis.
        Returns: None bei Erfolg, Fehlermeldung bei Fehler.
        """
        gid = self._normalize_product_gid(shopify_product_id)
        if not gid:
            return "Keine gültige Shopify-Produkt-ID."
        artist = (record_data.get("artist") or "").strip()
        title = (record_data.get("title") or "").strip()
        artist = _normalize_trailing_parens(artist)
        title = _normalize_trailing_parens(title)
        if not artist or not title:
            return "Artist und Title sind erforderlich."
        product_title = f"{artist} - {title}"
        description_html = self._build_description_html(record_data)
        label = (record_data.get("label") or "").strip()
        catalog_number = (record_data.get("cat_no") or "").strip()
        media = (record_data.get("media_condition") or "").strip()
        sleeve = (record_data.get("sleeve_condition") or "").strip()
        condition_str = "/".join(filter(None, [media, sleeve])) or "N/A"
        category = (record_data.get("shopify_category") or "").strip()
        metafields = [
            {"namespace": "vinyl", "key": "artist", "type": "single_line_text_field", "value": artist},
            {"namespace": "vinyl", "key": "label", "type": "single_line_text_field", "value": label or ""},
            {"namespace": "vinyl", "key": "condition", "type": "single_line_text_field", "value": condition_str},
            {"namespace": "vinyl", "key": "catalog_number", "type": "single_line_text_field", "value": catalog_number},
            {"namespace": "vinyl", "key": "product_category", "type": "single_line_text_field", "value": category or ""},
        ]
        price = record_data.get("pricing") or 0
        try:
            price_str = f"{float(price):.2f}"
        except (TypeError, ValueError):
            price_str = "0.00"
        update_product_mutation = """
        mutation productUpdate($product: ProductUpdateInput!) {
            productUpdate(product: $product) {
                product { id }
                userErrors { field message }
            }
        }
        """
        product_input = {
            "id": gid,
            "title": product_title,
            "descriptionHtml": description_html,
            "vendor": label or "Vinyl",
            "metafields": metafields,
        }
        category_id = self._resolve_taxonomy_category_id(category or self.DEFAULT_VINYL_CATEGORY_NAME)
        if category_id:
            product_input["category"] = category_id
            product_input["deleteConflictingConstrainedMetafields"] = True
            _log.info("Shopify Kategorie gesendet (Update): %s", category_id)
        try:
            data = self.execute_query(update_product_mutation, {"product": product_input})
        except RuntimeError as e:
            return str(e)
        err = self._extract_user_errors(data, "productUpdate")
        if err:
            return err
        self._fetch_product_category(gid)
        variant_id = self._get_variant_id_for_product(gid)
        if not variant_id:
            return "Produkt aktualisiert, aber Variante für Preis-Update nicht gefunden."
        update_variant_mutation = """
        mutation productVariantsBulkUpdate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
            productVariantsBulkUpdate(productId: $productId, variants: $variants) {
                productVariants { id }
                userErrors { field message }
            }
        }
        """
        variant_input = {
            "id": variant_id,
            "price": price_str,
            "taxable": False,
        }
        try:
            update_data = self.execute_query(update_variant_mutation, {
                "productId": gid,
                "variants": [variant_input],
            })
        except RuntimeError as e:
            return f"Produkt aktualisiert, Preis-Update fehlgeschlagen: {e}"
        update_err = self._extract_user_errors(update_data, "productVariantsBulkUpdate")
        if update_err:
            return f"Produkt aktualisiert, Preis-Update: {update_err}"
        # Produkt auf Verkaufskanal „Online Store“ veröffentlichen (bleibt im Shop sichtbar)
        pub_err = self.publish_product_to_online_store(gid)
        if pub_err:
            _log.warning("Produkt aktualisiert, Veröffentlichung auf Online Store: %s", pub_err)
        return None

    def get_inventory_available_for_product(self, shopify_product_id: str) -> Tuple[Optional[int], Optional[str]]:
        """
        Liest die verfügbare Menge (available) für ein Produkt aus Shopify.
        Nutzt die erste Variante und den ersten Inventory-Level (erste Location).
        
        Returns:
            (quantity, error_message)
            - (int, None): Erfolg, quantity ist die verfügbare Menge (0 wenn keine Levels).
            - (0, None): Produkt nicht gefunden oder keine Inventory-Levels.
            - (None, str): API-Fehler; str ist die Shopify-Fehlermeldung.
        """
        gid = self._normalize_product_gid(shopify_product_id)
        if not gid:
            return (None, "Keine gültige Shopify-Produkt-ID.")
        query = """
        query productInventory($id: ID!) {
            node(id: $id) {
                ... on Product {
                    variants(first: 1) {
                        nodes {
                            inventoryItem {
                                inventoryLevels(first: 5) {
                                    edges {
                                        node {
                                            quantities(names: ["available"]) {
                                                name
                                                quantity
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        try:
            data = self.execute_query(query, {"id": gid})
        except RuntimeError as e:
            return (None, str(e))
        node = (data.get("data") or {}).get("node")
        # node kann null sein (Produkt gelöscht/nicht gefunden) – dann 0 zurückgeben
        if not isinstance(node, dict):
            return (0, None)
        variants = node.get("variants", {}).get("nodes", [])
        if not variants or not isinstance(variants[0], dict):
            return (0, None)
        inv_item = variants[0].get("inventoryItem")
        if not isinstance(inv_item, dict):
            return (0, None)
        edges = inv_item.get("inventoryLevels", {}).get("edges", [])
        if not edges or not isinstance(edges[0], dict):
            return (0, None)
        level = edges[0].get("node")
        if not isinstance(level, dict):
            return (0, None)
        # InventoryLevel.quantities(names: ["available"]) → [{ name, quantity }]
        quantities = level.get("quantities") or []
        available = 0
        for q in quantities:
            if isinstance(q, dict) and q.get("name") == "available":
                try:
                    available = int(q.get("quantity", 0))
                except (TypeError, ValueError):
                    pass
                break
        return (available, None)

    def delete_product(self, shopify_product_id: str) -> Tuple[bool, Optional[str]]:
        """
        Löscht ein Produkt dauerhaft in Shopify (productDelete).
        Benötigt write_products. Die Löschung ist endgültig.

        Returns:
            (True, None): Erfolg.
            (False, str): Fehler; str ist die Fehlermeldung.
        """
        gid = self._normalize_product_gid(shopify_product_id)
        if not gid:
            return (False, "Keine gültige Shopify-Produkt-ID.")
        mutation = """
        mutation productDelete($input: ProductDeleteInput!) {
            productDelete(input: $input) {
                deletedProductId
                userErrors { field message }
            }
        }
        """
        try:
            data = self.execute_query(mutation, {"input": {"id": gid}})
        except RuntimeError as e:
            return (False, str(e))
        payload = (data.get("data") or {}).get("productDelete")
        if not isinstance(payload, dict):
            return (False, "Ungültige API-Antwort.")
        err = self._extract_user_errors(data, "productDelete")
        if err:
            return (False, err)
        if payload.get("deletedProductId"):
            return (True, None)
        return (False, "Produkt wurde nicht gelöscht (unbekannter Fehler).")

    def get_product_details_for_sync(self, shopify_product_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Liest Produktdaten (Preis, Titel, Beschreibung, Vendor, Vinyl-Metafields) aus Shopify
        für die Übernahme ins lokale Inventar.
        
        Returns:
            (record_data, error_message)
            - (dict, None): Erfolg; dict enthält pricing, artist, title, label, cat_no,
              media_condition, sleeve_condition, tracklist.
            - (None, str): Fehler; str ist die Fehlermeldung.
        """
        gid = self._normalize_product_gid(shopify_product_id)
        if not gid:
            return (None, "Keine gültige Shopify-Produkt-ID.")
        query = """
        query productDetailsForSync($id: ID!) {
            node(id: $id) {
                ... on Product {
                    title
                    descriptionHtml
                    vendor
                    metafields(first: 10, namespace: "vinyl") {
                        nodes { key value }
                    }
                    variants(first: 1) {
                        nodes { price }
                    }
                }
            }
        }
        """
        try:
            data = self.execute_query(query, {"id": gid})
        except RuntimeError as e:
            return (None, str(e))
        node = (data.get("data") or {}).get("node")
        if not isinstance(node, dict):
            return (None, "Produkt in Shopify nicht gefunden.")
        title_full = (node.get("title") or "").strip()
        description_html = node.get("descriptionHtml") or ""
        vendor = (node.get("vendor") or "").strip()
        metafields = node.get("metafields", {}).get("nodes", [])
        mf = {}
        for n in metafields:
            if isinstance(n, dict) and n.get("key") is not None:
                mf[n["key"]] = (n.get("value") or "").strip()
        artist = mf.get("artist", "").strip()
        title_from_mf = mf.get("title", "").strip()
        label = mf.get("label", "").strip() or vendor
        cat_no = mf.get("catalog_number", "").strip()
        condition_str = (mf.get("condition") or "").strip()
        if " – " in title_full:
            parts = title_full.split(" – ", 1)
            if not artist:
                artist = (parts[0] or "").strip()
            title = (title_from_mf or (parts[1] or "").strip() if len(parts) > 1 else title_full).strip()
        else:
            if not artist:
                artist = ""
            title = (title_from_mf or title_full).strip()
        media_condition = condition_str
        sleeve_condition = condition_str
        if "/" in condition_str:
            segs = condition_str.split("/", 1)
            media_condition = (segs[0] or "").strip()
            sleeve_condition = (segs[1] or "").strip() if len(segs) > 1 else media_condition
        variants = node.get("variants", {}).get("nodes", [])
        price_str = None
        if variants and isinstance(variants[0], dict):
            price_str = variants[0].get("price")
        try:
            pricing = float(price_str) if price_str is not None else 0.0
        except (TypeError, ValueError):
            pricing = 0.0
        # Tracklist als Klartext speichern (nicht HTML), damit die Bearbeitungsansicht korrekt parst
        tracklist_plain = html_to_tracklist_text(description_html) if description_html else ""
        record_data = {
            "pricing": pricing,
            "artist": artist or "",
            "title": title or title_full,
            "label": label or "",
            "cat_no": cat_no or "",
            "media_condition": media_condition or "",
            "sleeve_condition": sleeve_condition or "",
            "tracklist": tracklist_plain or "",
        }
        return (record_data, None)
    
    def create_vinyl_product(
        self,
        record_data: Dict[str, Any],
        image_paths: Optional[List[str]] = None,
        base_dir: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Erstellt ein Vinyl-Produkt in Shopify. Optional: Bilder per Staged-Upload anhängen.
        
        Args:
            record_data: Dictionary mit artist, title, tracklist, id, pricing, label,
                        media_condition, sleeve_condition, cat_no, year, etc.
            image_paths: Optionale Liste absoluter oder relativer Bildpfade (nur existierende werden hochgeladen).
            base_dir: Basisverzeichnis zur Auflösung relativer Pfade (z.B. BASE_DIR).
        
        Returns:
            (shopify_product_id, error_message, publication_warning)
            - Bei Erfolg: (product_id, None, None) oder (product_id, None, pub_warning) wenn Veröffentlichung fehlschlägt.
            - Bei Fehler: (None, error_message, None) oder (product_id, error_message, None).
        """
        artist = (record_data.get("artist") or "").strip()
        title = (record_data.get("title") or "").strip()
        artist = _normalize_trailing_parens(artist)
        title = _normalize_trailing_parens(title)
        if not artist or not title:
            return (None, "Artist und Title sind erforderlich.", None)
        
        product_title = f"{artist} - {title}"
        
        # Description: Metadaten, Titelliste (gruppiert), Zustandsbeschreibung
        description_html = self._build_description_html(record_data)
        
        # Condition + Metafields (label/catalog_number für Metafields und vendor)
        label = (record_data.get("label") or "").strip()
        catalog_number = (record_data.get("cat_no") or "").strip()
        media = (record_data.get("media_condition") or "").strip()
        sleeve = (record_data.get("sleeve_condition") or "").strip()
        condition_str = "/".join(filter(None, [media, sleeve])) or "N/A"
        category = (record_data.get("shopify_category") or "").strip()
        metafields = [
            {"namespace": "vinyl", "key": "artist", "type": "single_line_text_field", "value": artist},
            {"namespace": "vinyl", "key": "label", "type": "single_line_text_field", "value": label or ""},
            {"namespace": "vinyl", "key": "condition", "type": "single_line_text_field", "value": condition_str},
            {"namespace": "vinyl", "key": "catalog_number", "type": "single_line_text_field", "value": catalog_number},
            {"namespace": "vinyl", "key": "product_category", "type": "single_line_text_field", "value": category or ""},
        ]
        
        # Duplikatprüfung: bestehendes Produkt mit gleicher catalog_number wiederverwenden
        if catalog_number:
            existing_id = self._find_product_by_catalog_number(catalog_number)
            if existing_id:
                return (existing_id, None, None)
        
        local_id = record_data.get("id")
        sku = str(local_id) if local_id is not None else ""
        price = record_data.get("pricing") or 0
        quantity = record_data.get("quantity")
        if quantity is not None:
            try:
                quantity = max(0, int(quantity))
            except (TypeError, ValueError):
                quantity = 1
        else:
            quantity = 1
        try:
            price_str = f"{float(price):.2f}"
        except (TypeError, ValueError):
            price_str = "0.00"
        
        create_mutation = """
        mutation productCreate($product: ProductCreateInput!) {
            productCreate(product: $product) {
                product {
                    id
                    variants(first: 1) {
                        nodes {
                            id
                        }
                    }
                }
                userErrors { field message }
            }
        }
        """
        
        product_input = {
            "title": product_title,
            "descriptionHtml": description_html,
            "vendor": label or "Vinyl",
            "productType": "Vinyl",
            "metafields": metafields,
            "status": "ACTIVE",
        }
        category_id = self._resolve_taxonomy_category_id(category or self.DEFAULT_VINYL_CATEGORY_NAME)
        if category_id:
            product_input["category"] = category_id
            _log.info("Shopify Kategorie gesendet (Create): %s", category_id)

        try:
            data = self.execute_query(create_mutation, {"product": product_input})
        except RuntimeError as e:
            return (None, str(e), None)
        
        err_msg = self._extract_user_errors(data, "productCreate")
        if err_msg:
            return (None, err_msg, None)
        
        result = data.get("data", {}).get("productCreate", {})
        product = result.get("product")
        if not product:
            return (None, "Produkt wurde nicht erstellt.", None)
        
        product_id = product.get("id")
        if product_id:
            self._fetch_product_category(product_id)
        variants = product.get("variants", {}).get("nodes", [])
        variant_id = variants[0].get("id") if variants else None
        
        if not variant_id:
            pub_err = self.publish_product_to_online_store(product_id)
            if pub_err:
                _log.warning("Produkt erstellt, Veröffentlichung auf Online Store fehlgeschlagen: %s", pub_err)
            return (product_id, None, pub_err)  # Produkt erstellt, Variant-Update optional
        
        # Variante mit Preis, SKU und taxable aktualisieren
        update_mutation = """
        mutation productVariantsBulkUpdate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
            productVariantsBulkUpdate(productId: $productId, variants: $variants) {
                productVariants { id }
                userErrors { field message }
            }
        }
        """
        inventory_item = {"sku": sku, "tracked": True} if sku else {"tracked": True}
        variant_input = {
            "id": variant_id,
            "price": price_str,
            "taxable": False,
            "inventoryItem": inventory_item,
        }
        variant_input = {k: v for k, v in variant_input.items() if v is not None}
        
        try:
            update_data = self.execute_query(update_mutation, {
                "productId": product_id,
                "variants": [variant_input],
            })
        except RuntimeError as e:
            return (product_id, f"Produkt erstellt, aber Variant-Update fehlgeschlagen: {e}", None)
        
        update_err = self._extract_user_errors(update_data, "productVariantsBulkUpdate")
        if update_err:
            return (product_id, f"Produkt erstellt, aber Variant-Update: {update_err}", None)
        
        # Stückzahl in Shopify setzen (erste Location)
        qty_err = self.set_inventory_quantity(variant_id, quantity)
        if qty_err:
            return (product_id, f"Produkt erstellt, Stückzahl in Shopify konnte nicht gesetzt werden: {qty_err}", None)
        
        # Optionale Bilder: Staged-Upload pro Datei, dann productCreateMedia
        if image_paths:
            base = Path(base_dir).resolve() if base_dir else Path.cwd()
            resource_urls: List[str] = []
            upload_errors: List[str] = []
            for raw_path in image_paths:
                p = Path(raw_path).resolve() if Path(raw_path).is_absolute() else (base / raw_path)
                if not p.is_file():
                    continue
                resource_url, err = self._upload_image_to_staged(str(p))
                if err:
                    upload_errors.append(f"{p.name}: {err}")
                elif resource_url:
                    resource_urls.append(resource_url)
            if resource_urls:
                media_inputs = [
                    {"originalSource": url, "mediaContentType": "IMAGE", "alt": product_title}
                    for url in resource_urls
                ]
                media_err = self.add_product_media(product_id, media_inputs)
                if media_err:
                    upload_errors.append(media_err)
            if upload_errors:
                return (product_id, "Produkt erstellt, Bild-Upload fehlgeschlagen: " + "; ".join(upload_errors), None)
        
        # Produkt auf Verkaufskanal „Online Store“ veröffentlichen (im Shop sichtbar)
        pub_err = self.publish_product_to_online_store(product_id)
        if pub_err:
            _log.warning("Produkt erstellt, Veröffentlichung auf Online Store fehlgeschlagen: %s", pub_err)
        
        return (product_id, None, pub_err)
