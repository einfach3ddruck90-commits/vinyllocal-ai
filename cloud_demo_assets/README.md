# Cloud-Demo-Assets

Dieser Ordner wird für das **Cloud-Demo-Deployment** (Streamlit Community Cloud / Hugging Face Spaces) mit ins Repo übernommen.

- **vinyl_demo.db** – Gemeinsame Demo-Datenbank (Kunden, optional Inventar, Company Settings inkl. Platzhalter für Shopify Demo-Store).
- **vinyl_images/** – Cover-Bilder für das Demo-Inventar (optional befüllbar).

## Erstellung / Aktualisierung der Demo-DB

Einmalig oder bei Bedarf vom Projektroot aus ausführen:

```bash
python scripts/seed_cloud_demo_db.py
```

Das Skript erstellt bzw. überschreibt `vinyl_demo.db` mit Schema und voreingestellten Demo-Kunden. Vor dem Deploy können Sie in den Einstellungen der App (oder per DB-Update) den **Shopify Demo-Store** (Option A) eintragen: `shopify_enabled=1`, `shopify_store_url`, `shopify_access_token` in `company_settings`.

## .gitignore

`cloud_demo_assets/` wird nicht ignoriert. Ausnahmen in der Projekt-.gitignore erlauben das Committen von `vinyl_demo.db` und `vinyl_images/` nur in diesem Ordner.
