# IT Inventory Tracker (Windows-ready)

Simple Electron desktop app for IT teams to:

- Track inventory assets.
- Track who each asset is assigned to.
- Track purchase requests and who placed each order.

## Features

- Employee directory.
- Inventory table with assignment status.
- Re-assignment workflow for existing items.
- Purchase order log with requestor and purchaser fields.
- Local JSON persistence in Electron `userData` folder.

## Run locally

```bash
npm install
npm start
```

## Package for Windows

From any OS (cross-compile target configured):

```bash
npm run pack:win
```

Output artifact is generated in `dist/` as a Windows portable executable.

## Data location

App data is saved as `inventory-data.json` in Electron's per-user app data folder.
