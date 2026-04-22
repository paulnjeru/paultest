const state = {
  employees: [],
  items: [],
  orders: []
};

const employeeForm = document.getElementById('employee-form');
const itemForm = document.getElementById('item-form');
const assignForm = document.getElementById('assign-form');
const orderForm = document.getElementById('order-form');

function employeeName(employeeId) {
  return state.employees.find((e) => e.id === employeeId)?.name || '—';
}

function refreshSelects() {
  const employeeOptions = state.employees
    .map((e) => `<option value="${e.id}">${e.name}</option>`)
    .join('');

  document.getElementById('item-assignee').innerHTML =
    '<option value="">Unassigned</option>' + employeeOptions;

  const assignEmployee = document.getElementById('assign-employee');
  assignEmployee.innerHTML = employeeOptions;

  document.getElementById('order-requestor').innerHTML = employeeOptions;
  document.getElementById('order-purchaser').innerHTML = employeeOptions;

  const itemOptions = state.items
    .map((item) => `<option value="${item.id}">${item.assetTag} - ${item.name}</option>`)
    .join('');
  document.getElementById('assign-item').innerHTML = itemOptions;
}

function renderEmployees() {
  document.getElementById('employees-body').innerHTML = state.employees
    .map(
      (e) => `
      <tr>
        <td>${e.name}</td>
        <td>${e.department}</td>
        <td>${e.email}</td>
      </tr>`
    )
    .join('');
}

function renderItems() {
  document.getElementById('items-body').innerHTML = state.items
    .map(
      (i) => `
      <tr>
        <td>${i.assetTag}</td>
        <td>${i.name}</td>
        <td>${i.category}</td>
        <td>${i.status}</td>
        <td>${employeeName(i.assignedTo)}</td>
      </tr>`
    )
    .join('');
}

function renderOrders() {
  document.getElementById('orders-body').innerHTML = state.orders
    .map(
      (o) => `
      <tr>
        <td>${o.itemName}</td>
        <td>${o.quantity}</td>
        <td>${o.vendor}</td>
        <td>${employeeName(o.requestedBy)}</td>
        <td>${employeeName(o.orderedBy)}</td>
        <td>${o.status}</td>
        <td>${o.orderedDate}</td>
      </tr>`
    )
    .join('');
}

function renderAll() {
  renderEmployees();
  renderItems();
  renderOrders();
  refreshSelects();
}

async function init() {
  const data = await window.api.loadData();
  Object.assign(state, data);
  renderAll();
}

employeeForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = new FormData(employeeForm);
  const payload = Object.fromEntries(form.entries());
  await window.api.addEmployee(payload);
  const data = await window.api.loadData();
  Object.assign(state, data);
  renderAll();
  employeeForm.reset();
});

itemForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = new FormData(itemForm);
  const payload = Object.fromEntries(form.entries());
  await window.api.addItem(payload);
  const data = await window.api.loadData();
  Object.assign(state, data);
  renderAll();
  itemForm.reset();
});

assignForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const itemId = document.getElementById('assign-item').value;
  const employeeId = document.getElementById('assign-employee').value;
  await window.api.assignItem({ itemId, employeeId });
  const data = await window.api.loadData();
  Object.assign(state, data);
  renderAll();
});

orderForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = new FormData(orderForm);
  const payload = Object.fromEntries(form.entries());
  await window.api.addOrder(payload);
  const data = await window.api.loadData();
  Object.assign(state, data);
  renderAll();
  orderForm.reset();
});

init();
