const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  loadData: () => ipcRenderer.invoke('data:load'),
  addEmployee: (employee) => ipcRenderer.invoke('employee:add', employee),
  addItem: (item) => ipcRenderer.invoke('item:add', item),
  assignItem: (payload) => ipcRenderer.invoke('item:assign', payload),
  addOrder: (order) => ipcRenderer.invoke('order:add', order)
});
