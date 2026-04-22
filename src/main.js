const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');

const DB_FILE = 'inventory-data.json';

function getDbPath() {
  return path.join(app.getPath('userData'), DB_FILE);
}

function defaultData() {
  return {
    employees: [],
    items: [],
    orders: []
  };
}

function readData() {
  const dbPath = getDbPath();
  if (!fs.existsSync(dbPath)) {
    const initial = defaultData();
    fs.writeFileSync(dbPath, JSON.stringify(initial, null, 2));
    return initial;
  }

  const raw = fs.readFileSync(dbPath, 'utf8');
  return JSON.parse(raw);
}

function writeData(data) {
  const dbPath = getDbPath();
  fs.writeFileSync(dbPath, JSON.stringify(data, null, 2));
}

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    }
  });

  mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));
}

ipcMain.handle('data:load', async () => readData());

ipcMain.handle('employee:add', async (_event, employee) => {
  const db = readData();
  const newEmployee = {
    id: crypto.randomUUID(),
    ...employee
  };
  db.employees.push(newEmployee);
  writeData(db);
  return newEmployee;
});

ipcMain.handle('item:add', async (_event, item) => {
  const db = readData();
  const newItem = {
    id: crypto.randomUUID(),
    status: item.assignedTo ? 'Assigned' : 'Available',
    ...item
  };
  db.items.push(newItem);
  writeData(db);
  return newItem;
});

ipcMain.handle('item:assign', async (_event, { itemId, employeeId }) => {
  const db = readData();
  const item = db.items.find((x) => x.id === itemId);
  if (!item) {
    throw new Error('Item not found');
  }

  item.assignedTo = employeeId;
  item.status = employeeId ? 'Assigned' : 'Available';
  writeData(db);
  return item;
});

ipcMain.handle('order:add', async (_event, order) => {
  const db = readData();
  const newOrder = {
    id: crypto.randomUUID(),
    ...order
  };
  db.orders.push(newOrder);
  writeData(db);
  return newOrder;
});

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
