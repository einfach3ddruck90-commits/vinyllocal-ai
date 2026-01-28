╔══════════════════════════════════════════════════════════════╗
║           PORTABLE PYTHON - DOWNLOAD-ANLEITUNG              ║
╚══════════════════════════════════════════════════════════════╝

Dieser Ordner ist für portable Python vorgesehen.
Sie müssen portable Python hierher entpacken.

═══════════════════════════════════════════════════════════════

WINDOWS - WINPYTHON (EMPFOHLEN):
─────────────────────────────────

1. Besuchen Sie: https://winpython.github.io/
2. Laden Sie "WinPython 3.11" oder höher herunter
   → Wählen Sie die "64bit" Version
   → Datei: WinPython64-3.11.x.x.exe (oder .zip)
3. Entpacken Sie die Datei
4. Kopieren Sie den gesamten Inhalt des entpackten Ordners
   → In diesen Ordner: python_portable\
5. Die Struktur sollte sein:
   python_portable\
   ├── python.exe          ← WICHTIG: Muss vorhanden sein!
   ├── pythonw.exe
   ├── Scripts\
   │   └── pip.exe
   └── ...

ALTERNATIVE FÜR WINDOWS:
─────────────────────────

Portable Python:
- https://portablepython.com/
- Laden Sie Python 3.8+ herunter
- Entpacken Sie nach: python_portable\

═══════════════════════════════════════════════════════════════

LINUX/MAC:
──────────

1. Besuchen Sie: https://www.python.org/downloads/
2. Laden Sie Python 3.8+ herunter
3. Entpacken Sie nach: python_portable/
4. Die Struktur sollte sein:
   python_portable/
   └── bin/
       └── python3

ALTERNATIVE FÜR LINUX/MAC:
───────────────────────────

pyenv (empfohlen für portable Installation):
- https://github.com/pyenv/pyenv
- Installiert Python in: ~/.pyenv/versions/
- Kann für portable Nutzung konfiguriert werden

═══════════════════════════════════════════════════════════════

PRÜFUNG:
────────

Nach dem Entpacken sollte existieren:

WINDOWS:
  python_portable\python.exe

LINUX/MAC:
  python_portable\bin\python3

Falls diese Dateien nicht vorhanden sind, wurde Python
nicht korrekt entpackt.

═══════════════════════════════════════════════════════════════

DOWNLOAD-LINKS:
───────────────

WinPython (Windows, empfohlen):
  https://winpython.github.io/

Portable Python (Windows):
  https://portablepython.com/

Python.org (alle Plattformen):
  https://www.python.org/downloads/

═══════════════════════════════════════════════════════════════

HINWEISE:
─────────

- Portable Python wird NICHT mit der App mitgeliefert
- Sie müssen es selbst herunterladen (Dateigröße ~100-200 MB)
- Nach dem Entpacken funktioniert alles automatisch
- START_HIER.bat prüft automatisch ob Python vorhanden ist

═══════════════════════════════════════════════════════════════
