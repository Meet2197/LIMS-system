const token = () => localStorage.getItem('token');
if(!token()){ window.location.href='/login.html'; }

document.getElementById('logoutBtn').addEventListener('click', ()=>{ localStorage.removeItem('token'); window.location.href='/login.html'; });

const entityList = document.getElementById('entityList');
const contentArea = document.getElementById('contentArea');
let currentEntity = 'users';

entityList.addEventListener('click', (e)=>{
  const a = e.target.closest('a[data-entity]');
  if(!a) return;
  [...entityList.querySelectorAll('a')].forEach(x=>x.classList.remove('active'));
  a.classList.add('active');
  currentEntity = a.dataset.entity;
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
  users: {fields:[{k:'username',label:'Username'},{k:'password',label:'Password',type:'password'},{k:'fullname',label:'Full name'},{k:'affiliation',label:'Affiliation'},{k:'note',label:'Note'}]},
  materials:{fields:[{k:'matid',label:'Material ID'},{k:'interusername',label:'Internal user'},{k:'name',label:'Name'},{k:'species',label:'Species'},{k:'note',label:'Note'}]},
  gels:{fields:[{k:'gelid',label:'Gel ID'},{k:'gelname',label:'Gel name'},{k:'geltype',label:'Gel type'},{k:'note',label:'Note'}]},
  plates:{fields:[{k:'plateid',label:'Plate ID'},{k:'platename',label:'Plate name'},{k:'platenumber',label:'Plate number'}]},
  analysis:{fields:[{k:'analid',label:'Analysis ID'},{k:'anatype',label:'Type'},{k:'note',label:'Note'}]},
  methods:{fields:[{k:'metid',label:'Method ID'},{k:'methname',label:'Method name'},{k:'note',label:'Note'}]},
  proteomes:{fields:[{k:'mapid',label:'Map ID'},{k:'species',label:'Species'},{k:'note',label:'Note'}]}
};

function loadEntity(entity){
  const cfg = entityConfigs[entity];
  contentArea.innerHTML = '';
  const formCard = document.createElement('div');
  formCard.className = 'card-form mb-3';
  const form = document.createElement('form');
  form.id = 'form-' + entity;
  form.innerHTML = '<h5>Create / Edit ' + entity + '</h5>';
  cfg.fields.forEach(f=>{
    const div = document.createElement('div');
    div.className='mb-2';
    const inputType = f.type || 'text';
    div.innerHTML = `<input class="form-control" name="${f.k}" placeholder="${f.label}" type="${inputType}">`;
    form.appendChild(div);
  });
  form.innerHTML += '<div class="d-flex gap-2"><button class="btn btn-success" type="submit">Save</button><button id="clearBtn" class="btn btn-secondary" type="button">Clear</button></div>';
  formCard.appendChild(form);
  contentArea.appendChild(formCard);

  const listCard = document.createElement('div');
  listCard.className = 'card-form';
  listCard.innerHTML = '<h5>Existing ' + entity + '</h5><div id="list-'+entity+'">Loading...</div>';
  contentArea.appendChild(listCard);

  api(entity).then(async res=>{
    if(!res.ok){ document.getElementById('list-' + entity).innerText = 'Error loading'; return; }
    const items = await res.json();
    renderList(entity, items);
  });

  let editingId = null;
  form.addEventListener('submit', async function(e){
    e.preventDefault();
    const data = Object.fromEntries(new FormData(this).entries());
    if(editingId){
      const res = await api(entity + '/' + editingId, {method:'PUT', body:data});
      if(res.ok){ alert('Updated'); editingId=null; form.reset(); loadEntity(entity); }
      else alert('Update failed');
    } else {
      const res = await api(entity, {method:'POST', body:data});
      if(res.ok){ alert('Saved'); form.reset(); loadEntity(entity); }
      else alert('Save failed');
    }
  });
  document.getElementById('clearBtn').addEventListener('click', ()=>{ editingId=null; form.reset(); });

  function renderList(entity, items){
    const container = document.getElementById('list-' + entity);
    if(!items.length){ container.innerHTML = '<div class="text-muted">No records</div>'; return; }
    const table = document.createElement('table');
    table.className = 'table table-sm';
    const thead = document.createElement('thead');
    const headRow = document.createElement('tr');
    headRow.innerHTML = '<th>ID</th>' + cfg.fields.map(f=>`<th>${f.label}</th>`).join('') + '<th>Actions</th>';
    thead.appendChild(headRow);
    table.appendChild(thead);
    const tbody = document.createElement('tbody');
    items.forEach(it=>{
      const tr = document.createElement('tr');
      tr.innerHTML = '<td>' + it.id + '</td>' + cfg.fields.map(f=>`<td>${(it[f.k]||'')}</td>`).join('') + `<td class="table-actions">
        <button class="btn btn-sm btn-primary" data-id="${it.id}" data-action="edit">Edit</button>
        <button class="btn btn-sm btn-danger" data-id="${it.id}" data-action="delete">Delete</button>
      </td>`;
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    container.innerHTML = '';
    container.appendChild(table);

    container.querySelectorAll('button[data-action]').forEach(btn=>{
      btn.addEventListener('click', async function(){
        const id = this.dataset.id;
        const action = this.dataset.action;
        if(action==='edit'){
          const res = await api(entity + '/' + id);
          if(!res.ok){ alert('Not found'); return; }
          const obj = await res.json();
          editingId = id;
          const fm = document.getElementById('form-' + entity);
          cfg.fields.forEach(f=> fm.elements[f.k].value = obj[f.k] || '');
          window.scrollTo({top:0,behavior:'smooth'});
        } else if(action==='delete'){
          if(!confirm('Delete this record?')) return;
          const res = await api(entity + '/' + id, {method:'DELETE'});
          if(res.ok){ alert('Deleted'); loadEntity(entity); } else alert('Delete failed');
        }
      });
    });
  }
}

loadEntity(currentEntity);
