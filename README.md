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

## Build Windows EXE locally (on Windows)

```bat
scripts\build_windows.bat
```

Output:

- `dist\ITInventoryHub.exe`

## Build + Download Windows EXE from GitHub Actions

This repository includes a workflow at `.github/workflows/build-windows-exe.yml` that builds a Windows EXE on `windows-latest` and uploads it as an artifact.

### Steps to get the downloadable EXE

1. Push this branch to GitHub.
2. Open **Actions** tab.
3. Run **Build Windows EXE** (or use a push-triggered run).
4. Open the completed run.
5. Download artifact **ITInventoryHub-windows-exe**.
6. Extract to get `ITInventoryHub.exe`.

## Data storage

- SQLite DB: `data/inventory.db`
- Downloaded images: `assets/*.jpg`
