// client/admin.js
const API_BASE = window.location.origin;
const TOKEN_KEY = 'tf_admin_token';

const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[c]));

const newIdInput = document.getElementById('new-id');
const newTitleInput = document.getElementById('new-title');
const newThumbInput = document.getElementById('new-thumb');
const newCategoryInput = document.getElementById('new-category');
const newYearInput = document.getElementById('new-year');
const newDescriptionInput = document.getElementById('new-description');
const newFeaturedInput = document.getElementById('new-featured');
const tokenInput = document.getElementById('admin-token');
const addBtn = document.getElementById('add-btn');
const cancelBtn = document.getElementById('cancel-btn');
const refreshBtn = document.getElementById('refresh-btn');
const exportBtn = document.getElementById('export-btn');
const importBtn = document.getElementById('import-btn');
const importBox = document.getElementById('import-box');
const importTextarea = document.getElementById('import-textarea');
const confirmImportBtn = document.getElementById('confirm-import-btn');
const cancelImportBtn = document.getElementById('cancel-import-btn');
const idsList = document.getElementById('ids-list');
const formPanel = document.querySelector('.panel');

let editingId = null;
let cachedItems = [];

tokenInput.value = localStorage.getItem(TOKEN_KEY) || '';
tokenInput.addEventListener('input', () => localStorage.setItem(TOKEN_KEY, tokenInput.value.trim()));

function authHeaders() {
  const token = tokenInput.value.trim();
  return token ? { 'x-admin-token': token } : {};
}

function checkPersisted(data) {
  if (data && data.persisted === false) {
    alert('ATENÇÃO: a alteração foi aplicada apenas temporariamente e NÃO foi salva permanentemente.\n\n' +
      'Verifique no servidor (Vercel) as variáveis UPSTASH_REDIS_REST_URL e UPSTASH_REDIS_REST_TOKEN ' +
      'e faça um novo deploy. Você pode conferir em /api/health se o Redis está configurado.');
  }
}

async function fetchIds() {
  try {
    const res = await fetch(`${API_BASE}/api/ids`, { cache: 'no-store' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    return data.items || [];
  } catch (err) {
    console.error('Erro fetch ids', err);
    return [];
  }
}

function renderIds(items) {
  if (!items.length) {
    idsList.innerHTML = '<div class="empty-state">Nenhum vídeo no catálogo ainda.</div>';
    return;
  }
  idsList.innerHTML = items.map(item => {
    const thumb = item.thumb || `https://img.youtube.com/vi/${encodeURIComponent(item.id)}/hqdefault.jpg`;
    return `
      <div class="item">
        <img class="item-thumb" src="${esc(thumb)}" alt="" loading="lazy" onerror='this.onerror=null;this.src="https://img.youtube.com/vi/${encodeURIComponent(item.id)}/hqdefault.jpg"'>
        <div class="item-info">
          <strong>${esc(item.title || item.id)}</strong>
          ${item.featured ? '<small class="feat-badge">★ No destaque do topo</small>' : ''}
          ${item.title ? `<small>ID: ${esc(item.id)} · título do YouTube substituído</small>` : ''}
          <small>Categoria: ${esc(item.category || 'Diversos')}${item.year ? ' · Ano: ' + esc(item.year) : ''}</small>
          <small>Descrição: ${esc((item.description || '').substring(0, 70))}</small>
          <small>Thumbnail: ${item.thumb ? 'personalizada' : 'automática do YouTube'}</small>
        </div>
        <div class="item-actions">
          <button data-id="${esc(item.id)}" class="edit">Editar</button>
          <button data-id="${esc(item.id)}" class="remove">Remover</button>
        </div>
      </div>`;
  }).join('');
}

idsList.addEventListener('click', async e => {
  const editBtn = e.target.closest('.edit');
  if (editBtn) return startEdit(editBtn.dataset.id);
  const removeBtn = e.target.closest('.remove');
  if (removeBtn) await removeId(removeBtn.dataset.id);
});

function startEdit(id) {
  const it = cachedItems.find(x => x.id === id);
  if (!it) return;
  editingId = id;
  newIdInput.value = it.id;
  newIdInput.disabled = true;
  newTitleInput.value = it.title || '';
  newThumbInput.value = it.thumb || '';
  newCategoryInput.value = it.category || '';
  newYearInput.value = it.year || '';
  newDescriptionInput.value = it.description || '';
  newFeaturedInput.checked = Boolean(it.featured);
  addBtn.textContent = 'Salvar alterações';
  cancelBtn.style.display = '';
  formPanel.classList.add('editing');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function resetEdit() {
  editingId = null;
  newIdInput.disabled = false;
  newTitleInput.value = '';
  newThumbInput.value = '';
  newCategoryInput.value = '';
  newYearInput.value = '';
  newDescriptionInput.value = '';
  newFeaturedInput.checked = false;
  addBtn.textContent = 'Adicionar';
  cancelBtn.style.display = 'none';
  formPanel.classList.remove('editing');
}

cancelBtn.addEventListener('click', resetEdit);

async function loadAndRender() {
  cachedItems = await fetchIds();
  renderIds(cachedItems);
}

async function addId(id, thumb, title, category, description, featured, year) {
  try {
    const res = await fetch(`${API_BASE}/api/catalog/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ id, thumb, title, category, description, featured, year })
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || 'HTTP ' + res.status);
    checkPersisted(data);
    await loadAndRender();
    alert('ID adicionado com sucesso');
  } catch (err) {
    console.error('Erro ao adicionar', err);
    alert(err.message === '401' ? 'Token de administrador inválido ou ausente.' : `Erro ao adicionar: ${err.message}`);
  }
}

async function removeId(id) {
  if (!confirm('Remover ' + id + '?')) return;
  try {
    const res = await fetch(`${API_BASE}/api/catalog/remove`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ id })
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || 'HTTP ' + res.status);
    checkPersisted(data);
    await loadAndRender();
    alert('ID removido');
  } catch (err) {
    console.error('Erro ao remover', err);
    alert(`Erro ao remover: ${err.message}`);
  }
}

async function updateItem(id, thumb, title, category, description, featured, year) {
  try {
    const res = await fetch(`${API_BASE}/api/catalog/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ id, thumb, title, category, description, featured, year })
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || 'HTTP ' + res.status);
    checkPersisted(data);
    await loadAndRender();
    alert('Alterações salvas');
  } catch (err) {
    console.error('Erro ao salvar', err);
    alert(`Erro ao salvar: ${err.message}`);
  }
}

addBtn.addEventListener('click', () => {
  const id = (newIdInput.value || '').trim();
  const thumb = (newThumbInput.value || '').trim();
  const title = (newTitleInput.value || '').trim();
  const category = (newCategoryInput.value || '').trim();
  const year = (newYearInput.value || '').trim();
  const description = (newDescriptionInput.value || '').trim();
  const featured = newFeaturedInput.checked;

  if (editingId) {
    updateItem(editingId, thumb, title, category || 'Diversos', description, featured, year);
    resetEdit();
    return;
  }

  if (!id) return alert('Digite um ID');
  if (!/^[A-Za-z0-9_-]{11}$/.test(id)) return alert('ID inválido: deve ter exatamente 11 caracteres (letras, números, - ou _)');
  addId(id, thumb, title, category || 'Diversos', description, featured, year);
  newIdInput.value = '';
  newTitleInput.value = '';
  newThumbInput.value = '';
  newCategoryInput.value = '';
  newYearInput.value = '';
  newDescriptionInput.value = '';
  newFeaturedInput.checked = false;
});

refreshBtn.addEventListener('click', loadAndRender);

exportBtn.addEventListener('click', async () => {
  const items = await fetchIds();
  if (!items.length) return alert('Catálogo vazio, nada para exportar.');
  const blob = new Blob([JSON.stringify(items, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'catalogo-tubeflix.json';
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(a.href);
});

importBtn.addEventListener('click', () => {
  importBox.style.display = importBox.style.display === 'none' ? 'block' : 'none';
});

cancelImportBtn.addEventListener('click', () => {
  importBox.style.display = 'none';
  importTextarea.value = '';
});

confirmImportBtn.addEventListener('click', async () => {
  let parsed;
  try {
    parsed = JSON.parse(importTextarea.value);
  } catch (e) {
    return alert('JSON inválido. Cole exatamente o conteúdo exportado.');
  }
  const body = Array.isArray(parsed) ? { items: parsed } : parsed;
  if (!body || !Array.isArray(body.items)) return alert('Formato esperado: um array de vídeos ou { "items": [...] }.');
  if (!confirm(`Substituir TODO o catálogo atual pelos ${body.items.length} vídeos do JSON?`)) return;
  try {
    const res = await fetch(`${API_BASE}/api/catalog/import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(body)
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || 'HTTP ' + res.status);
    checkPersisted(data);
    importBox.style.display = 'none';
    importTextarea.value = '';
    await loadAndRender();
    alert(`Catálogo substituído: ${data.imported} vídeos importados.`);
  } catch (err) {
    console.error('Erro ao importar', err);
    alert(`Erro ao importar: ${err.message}`);
  }
});

window.addEventListener('load', loadAndRender);
