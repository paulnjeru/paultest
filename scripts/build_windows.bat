@echo off
python -m pip install -r requirements.txt
pyinstaller --noconfirm --windowed --onefile --name ITInventoryHub --add-data "assets;assets" run.py
echo Build complete. EXE is in dist\ITInventoryHub.exe
