# Automatische Stückzahl-Erhöhung bei Duplikat

## Problem

Wenn eine neue Platte gescannt wird und ein Duplikat gefunden wird, gibt es aktuell nur zwei Optionen:
1. Detailansicht anzeigen
2. Neue ID anlegen

Es fehlt eine Option, die Stückzahl automatisch zur bestehenden hinzuzufügen und das Inventar sofort zu aktualisieren.

## Lösung

### Phase 1: Button "Stückzahl erhöhen" hinzufügen (`app.py` ~Zeile 3630-3637)

**Aktuelles Verhalten:**
- Nur "Neue ID anlegen" Button im Form
- Keine Option zum automatischen Erhöhen der Stückzahl

**Neues Verhalten:**
- Neuer Button "Stückzahl erhöhen" im Form (vor "Neue ID anlegen")
- Beim Klick wird die Stückzahl des Duplikats erhöht
- Inventar wird sofort aktualisiert
- Scan-State wird zurückgesetzt

**Implementierung:**

Füge einen neuen Button im Form hinzu:

```python
# Form für Duplikat-Aktionen
form_key = f"duplicate_form_{duplicate.get('id')}_{item_data.get('cat_no', '')}"
with st.form(form_key):
    # NEUER Button: Stückzahl erhöhen
    increment_submitted = st.form_submit_button(
        f"➕ Stückzahl erhöhen\n(Addiere {item_data.get('quantity', 1)} zur bestehenden Stückzahl)",
        use_container_width=True,
        help="Erhöht die Stückzahl des bestehenden Eintrags um die gescannte Menge."
    )
    
    save_anyway_submitted = st.form_submit_button(
        f"💾 Neue ID anlegen\n(Als separates Item speichern)",
        use_container_width=True,
        help="Speichert die Platte als separates Item mit einer neuen ID."
    )

# Logik für "Stückzahl erhöhen" Button NACH dem Form-Block
if increment_submitted:
    duplicate_id = duplicate.get("id")
    quantity_to_add = item_data.get("quantity", 1)
    
    # Erhöhe Stückzahl des bestehenden Eintrags
    new_quantity = st.session_state.db.increment_inventory_quantity(duplicate_id, quantity_to_add)
    
    if new_quantity is not None:
        # Erfolg - zeige Erfolgsmeldung
        success_msg = f"✅ Stückzahl erhöht: {duplicate.get('quantity', 0)} → {new_quantity} (hinzugefügt: {quantity_to_add})"
        st.session_state.duplicate_success_message = success_msg
        
        # Entferne verarbeitetes Item aus Session State
        st.session_state.items_with_duplicates = [
            i for i in st.session_state.items_with_duplicates 
            if i != dup_info
        ]
        
        # Wenn keine Duplikate mehr vorhanden, setze Flag zurück
        if not st.session_state.items_with_duplicates:
            st.session_state.duplicate_found = False
        
        # Reset Scan-State
        reset_metadata()
        
        # Setze Flag für Inventar-Aktualisierung
        st.session_state.inventory_refresh_needed = True
        
        st.rerun()
    else:
        st.error("❌ Fehler beim Erhöhen der Stückzahl.")
```

### Phase 2: Inventar-Aktualisierung sicherstellen

**Änderungen:**
- Setze `st.session_state.inventory_refresh_needed = True` nach erfolgreicher Stückzahl-Erhöhung
- Stelle sicher, dass die Inventarliste die aktualisierten Werte anzeigt

## Dateien zu ändern

- `app.py`:
  - `show_scan_session()` Funktion (~Zeile 3630-3640) - Neuen Button "Stückzahl erhöhen" hinzufügen
  - Logik für Stückzahl-Erhöhung (~Zeile 3640-3700) - Nach dem Form-Block hinzufügen

## Test-Szenarien

1. **Duplikat gefunden**: Scanne Platte die bereits existiert → Button "Stückzahl erhöhen" sollte erscheinen
2. **Stückzahl erhöhen**: Klicke "Stückzahl erhöhen" → Stückzahl sollte erhöht werden, Inventar aktualisiert
3. **Mehrere Duplikate**: Wenn mehrere Duplikate vorhanden → Jedes sollte einzeln behandelt werden können
4. **Inventar aktualisiert**: Nach Stückzahl-Erhöhung → Inventarliste sollte neue Stückzahl anzeigen
5. **Scan-State zurückgesetzt**: Nach Stückzahl-Erhöhung → Scan-State sollte zurückgesetzt sein für neuen Scan
