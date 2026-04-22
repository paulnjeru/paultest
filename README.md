# IT Inventory & Procurement Hub (Python Desktop App)

A modern, Windows-friendly desktop app for IT teams to manage:

- **Inventory assets** (laptops, monitors, accessories, etc.)
- **Asset assignment** (who currently has each item)
- **Purchase workflow ownership** (who requested vs. who placed each order)

This version is built in **Python** (Tkinter + ttkbootstrap) so it is easy to package as a Windows `.exe` using **PyInstaller**.

## User-friendly GUI highlights

- Clean, modern theme with dashboard cards
- Tabbed workflow: Dashboard, Inventory, Employees, Orders
- Visual hero image section for a polished look
- Fast local storage with SQLite (no server required)

## Web graphics used

The app downloads these public images on first run into `assets/`:

1. Dell server image (Wikimedia Commons):
   - https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Dell_Servers.jpg/1280px-Dell_Servers.jpg
2. Laptop and mouse image (Wikimedia Commons):
   - https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/Laptop_and_mouse.jpg/1280px-Laptop_and_mouse.jpg

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

## Build Windows EXE

### Option A (simple)

```bash
pip install -r requirements.txt
pyinstaller --noconfirm --windowed --onefile --name ITInventoryHub --add-data "assets;assets" run.py
```

### Option B (script on Windows)

Run:

```bat
scripts\build_windows.bat
```

Your executable will be generated at:

- `dist/ITInventoryHub.exe`

## Data storage

- SQLite DB: `data/inventory.db`
- Downloaded images: `assets/*.jpg`
