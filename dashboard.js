const token = () => localStorage.getItem('token');
if(!token()){ window.location.href='/login.html'; }

document.getElementById('logoutBtn').addEventListener('click', ()=>{ localStorage.removeItem('token'); window.location.href='/login.html'; });

const entityList = document.getElementById('entityList');
const contentArea = document.getElementById('contentArea');
let currentEntity = 'users';
let editingId = null;

entityList.addEventListener('click', (e)=>{
  const a = e.target.closest('a[data-entity]');
  if(!a) return;
  [...entityList.querySelectorAll('a')].forEach(x=>x.classList.remove('active'));
  a.classList.add('active');
  currentEntity = a.dataset.entity;
  editingId = null; // Clear editing state when changing entity
  loadEntity(currentEntity);
});

function api(path, opts){
  opts = opts || {};
  opts.headers = opts.headers || {};
  opts.headers['Authorization'] = 'Bearer ' + token();
  if(opts.body && typeof opts.body === 'object' && !(opts.body instanceof FormData)){
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(opts.body);
  }
  return fetch('/api/' + path, opts);
}

const entityConfigs = {
  users: {
    fields:[
      {k:'username', label:'Username'},
      {k:'password', label:'Password', type:'password'},
      {k:'fullname', label:'Full name'},
      {k:'affiliation', label:'Affiliation'},
      {k:'note', label:'Note'}
    ]
  },
  materials:{
    fields:[
      {k:'matid',label:'Material ID'},
      {k:'interusername',label:'Username'},
      {k:'name',label:'Name'},
      {k:'species',label:'Species'},
      {k:'note',label:'Note'}
    ]
  },
  gels:{
    fields:[
      {k:'gelid',label:'Gel ID'},
      {k:'gelname',label:'Gel Name'},
      {k:'geltype',label:'Gel Type'},
      {k:'note',label:'Note'}
    ]
  },
  plates:{
    fields:[
      {k:'plateid',label:'Plate ID'},
      {k:'platename',label:'Plate Name'},
      {k:'platenumber',label:'Plate Number'}
    ]
  },
  analysis:{
    fields:[
      {k:'analid',label:'Analysis ID'},
      {k:'anatype',label:'Analysis Type'},
      {k:'note',label:'Note'}
    ]
  },
  methods:{
    fields:[
      {k:'metid',label:'Method ID'},
      {k:'methname',label:'Method Name'},
      {k:'note',label:'Note'}
    ]
  },
  proteomes:{
    fields:[
      {k:'mapid',label:'Map ID'},
      {k:'species',label:'Species'},
      {k:'note',label:'Note'}
    ]
  }
};

async function loadEntity(entity){
  const cfg = entityConfigs[entity];
  if(!cfg) return;

  // Clear existing content and display new title
  contentArea.innerHTML = '';
  const title = document.createElement('h2');
  title.className = 'mb-4';
  title.textContent = entity.charAt(0).toUpperCase() + entity.slice(1);
  contentArea.appendChild(title);

  // Create form
  const formCard = document.createElement('div');
  formCard.className = 'card card-form mb-4';
  const form = document.createElement('form');
  form.id = `form-${entity}`;
  form.innerHTML = `
    <div class="row">
      ${cfg.fields.map(f => `
        <div class="col-md-6 mb-3">
          <label for="${entity}-${f.k}" class="form-label">${f.label}</label>
          <input type="${f.type || 'text'}" id="${entity}-${f.k}" name="${f.k}" class="form-control" ${f.k === 'username' || f.k.includes('id') ? 'required' : ''}>
        </div>
      `).join('')}
    </div>
    <button type="submit" class="btn btn-primary">Save</button>
    <button type="reset" class="btn btn-secondary">Clear</button>
  `;
  formCard.appendChild(form);
  contentArea.appendChild(formCard);

  form.addEventListener('submit', async function(e){
    e.preventDefault();
    const data = Object.fromEntries(new FormData(this).entries());
    
    // Only send the password if it's not empty, for updates
    if (entity === 'users' && data.password === '') {
        delete data.password;
    }

    let res;
    if(editingId){
      res = await api(entity + '/' + editingId, {method:'PUT', body: data});
    } else {
      res = await api(entity, {method:'POST', body: data});
    }

    if(res.ok){
      console.log('Record saved successfully.');
      form.reset();
      editingId = null;
      loadEntity(entity);
    } else {
      const errorData = await res.json();
      console.error('Failed to save record:', errorData.msg);
    }
  });

  // Create table
  const tableContainer = document.createElement('div');
  tableContainer.id = `table-${entity}`;
  contentArea.appendChild(tableContainer);
  
  // Fetch and display data
  const res = await api(entity);
  if(!res.ok) {
    tableContainer.innerHTML = '<p>Error loading data.</p>';
    console.error('Error loading data:', await res.text());
    return;
  }
  const items = await res.json();
  const table = document.createElement('table');
  table.className = 'table table-striped table-hover';
  
  const thead = document.createElement('thead');
  thead.innerHTML = `<tr>
    <th>ID</th>
    ${cfg.fields.map(f=>`<th>${f.label}</th>`).join('')}
    <th>Actions</th>
  </tr>`;
  table.appendChild(thead);
  
  const tbody = document.createElement('tbody');
  items.forEach(it=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${it.id}</td>` + 
                   cfg.fields.map(f=>`<td>${f.type === 'password' ? '********' : (it[f.k] || '')}</td>`).join('') + 
                   `<td class="table-actions">
                      <button class="btn btn-sm btn-primary" data-id="${it.id}" data-action="edit">Edit</button>
                      <button class="btn btn-sm btn-danger" data-id="${it.id}" data-action="delete">Delete</button>
                   </td>`;
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  tableContainer.innerHTML = '';
  tableContainer.appendChild(table);

  tableContainer.querySelectorAll('button[data-action]').forEach(btn=>{
    btn.addEventListener('click', async function(){
      const id = this.dataset.id;
      const action = this.dataset.action;
      if(action==='edit'){
        const res = await api(entity + '/' + id);
        if(!res.ok){ console.error('Not found'); return; }
        const obj = await res.json();
        editingId = id;
        const fm = document.getElementById(`form-${entity}`);
        cfg.fields.forEach(f=> fm.elements[f.k].value = obj[f.k] || '');
        window.scrollTo({top:0,behavior:'smooth'});
      } else if(action==='delete'){
        console.log(`Deleting record with ID: ${id}`);
        const res = await api(entity + '/' + id, {method:'DELETE'});
        if(res.ok){
          console.log('Record deleted successfully.');
          loadEntity(entity);
        } else {
          console.error('Failed to delete record.');
        }
      }
    });
  });
}

// Initial load
loadEntity(currentEntity);
