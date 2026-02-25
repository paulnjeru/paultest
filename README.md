# Front Office Visitor Management System

A standalone desktop application (Python + Tkinter) for capturing visitor entries and generating periodic reports.

## Features
- Visitor entry form with mandatory fields:
  - Visitor's Name
  - Date of Visit (YYYY-MM-DD)
  - Time of Arrival (HH:MM)
  - Person Being Visited
  - Reason for Visit
- Local SQLite database storage (`visitor_management.db`)
- Report generation:
  - Daily
  - Weekly
  - Monthly
  - Yearly
- Built-in report statistics:
  - Total visits
  - Frequently visited personnel
  - Top reasons for visits
- Report export:
  - PDF
  - Excel (`.xlsx`)
- Basic user access controls:
  - `admin / admin123` → can add visitor entries and generate/export reports
  - `viewer / viewer123` → can only generate/export reports (submit disabled)

## Quick Start (Development)

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

## Build Installable `.exe` (Windows)

1. Install build dependency:
   ```bash
   pip install pyinstaller
   ```
2. Build single-file executable:
   ```bash
   pyinstaller --name VisitorManagement --onefile --windowed -p . app/main.py
   ```
3. Output executable will be available in:
   - `dist/VisitorManagement.exe`

## Suggested Installer Packaging
Use **Inno Setup** or **NSIS** to package `VisitorManagement.exe` into a guided installer.

## Testing

Run unit tests:

```bash
python -m unittest discover -s tests
```
