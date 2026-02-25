# User Manual - Front Office Visitor Management System

## 1. Installation
1. Copy `VisitorManagement.exe` to a Windows machine.
2. (Optional) Run installer if packaged with Inno Setup/NSIS.
3. Launch the app from desktop/start menu shortcut.

## 2. Login
- **Admin**
  - Username: `admin`
  - Password: `admin123`
  - Permission: Can submit visitor entries and generate/export reports.
- **Viewer**
  - Username: `viewer`
  - Password: `viewer123`
  - Permission: Can generate/export reports only.

## 3. Entering Visitor Data
1. Fill all required fields:
   - Visitor's Name
   - Date of Visit (YYYY-MM-DD)
   - Time of Arrival (HH:MM)
   - Person Being Visited
   - Reason for Visit
2. Click **Submit**.
3. A success message confirms data is saved.

### Validation Rules
- All fields are mandatory.
- Date must follow `YYYY-MM-DD` format.
- Time must follow `HH:MM` (24-hour) format.

## 4. Generating Reports
1. Select period: **Daily / Weekly / Monthly / Yearly**.
2. Click **Generate Report**.
3. Review statistics in the report panel:
   - Total visits
   - Frequently visited personnel
   - Top reasons for visits

## 5. Exporting Reports
- Click **Export PDF** to save a PDF report.
- Click **Export Excel** to save an `.xlsx` report.

Files are saved in the current working directory.

## 6. Troubleshooting
- **Validation error shown:** check date/time format and required fields.
- **No data in report:** ensure entries exist for the selected period.
- **Export blocked:** generate a report before exporting.
