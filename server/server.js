// server/server.js
const express = require('express');
const axios = require('axios');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 4000;
const CATALOG_FILE = path.join(__dirname, 'catalog.json');
const YOUTUBE_ID_RE = /^[A-Za-z0-9_-]{11}$/;
const IS_PROD = process.env.NODE_ENV === 'production';

// --- armazenamento: Upstash Redis REST (produção) ou arquivo JSON (local) ---
const REDIS_KEY = 'tubeflix:catalog';
const UPSTASH_URL = process.env.UPSTASH_REDIS_REST_URL;
const UPSTASH_TOKEN = process.env.UPSTASH_REDIS_REST_TOKEN;
const useRedis = Boolean(UPSTASH_URL && UPSTASH_TOKEN);

const DEFAULT_CATALOG = [
  { id: 'DGZsRoKYXPI', thumb: '', category: 'Filmes', description: 'Uma história de fuga emocionante' },
  { id: '2MRcOdjY-QE', thumb: '', category: 'Filmes', description: 'Drama com atuações incríveis' },
  { id: 'vcPr9USr2tA', thumb: '', category: 'Filmes', description: 'Suspense que te prende' },
  { id: '2Vv-BfVoq4g', thumb: '', category: 'Musicais', description: 'Clipe musical oficial' },
  { id: 'kXYiU_JCYtU', thumb: '', category: 'Musicais', description: 'Música clássica remasterizada' },
  { id: '3JZ_D3ELwOQ', thumb: '', category: 'Musicais', description: 'Novo lançamento' }
];

function normalizeItem(item) {
  if (typeof item === 'string') return { id: item, thumb: '', title: '', category: 'Diversos', description: '', featured: false };
  return {
    id: String(item.id || ''),
    thumb: typeof item.thumb === 'string' && /^https:\/\//.test(item.thumb) ? item.thumb : '',
    title: item.title || '',
    category: item.category || 'Diversos',
    description: item.description || '',
    year: String(item.year || '').trim(),
    featured: Boolean(item.featured)
  };
}

function readCatalogFile() {
  try {
    if (fs.existsSync(CATALOG_FILE)) {
      const data = JSON.parse(fs.readFileSync(CATALOG_FILE, 'utf8'));
      if (Array.isArray(data)) return data.map(normalizeItem);
    }
  } catch (e) {
    console.log('Arquivo catalog.json inválido, usando padrão');
  }
  return DEFAULT_CATALOG;
}

async function redisGet() {
  const res = await axios.get(`${UPSTASH_URL}/get/${REDIS_KEY}`, {
    headers: { Authorization: `Bearer ${UPSTASH_TOKEN}` },
    timeout: 5000
  });
  const raw = res.data && res.data.result;
  if (!raw) return null;
  // gravações são feitas com encodeURIComponent; aceita também JSON puro
  try { return JSON.parse(decodeURIComponent(raw)); }
  catch (e1) {
    try { return JSON.parse(raw); } catch (e2) { return null; }
  }
}

async function redisSet(items) {
  await axios.post(`${UPSTASH_URL}/set/${REDIS_KEY}`, encodeURIComponent(JSON.stringify(items)), {
    headers: { Authorization: `Bearer ${UPSTASH_TOKEN}` },
    timeout: 5000
  });
}

let CATALOG_ITEMS = [];

async function loadCatalog() {
  if (useRedis) {
    try {
      const remote = await redisGet();
      if (Array.isArray(remote)) return remote.map(normalizeItem);
    } catch (e) {
      console.log('Falha ao ler do Redis:', e.message);
    }
  }
  return readCatalogFile();
}

async function persistCatalog() {
  if (useRedis) {
    try {
      await redisSet(CATALOG_ITEMS);
      return true;
    } catch (e) {
      console.error('Falha ao salvar no Redis:', e.message);
      return false;
    }
  }
  if (!IS_PROD) {
    try {
      fs.writeFileSync(CATALOG_FILE, JSON.stringify(CATALOG_ITEMS, null, 2), 'utf8');
      return true;
    } catch (e) {
      console.error('Não foi possível salvar catalog.json:', e.message);
      return false;
    }
  }
  return false;
}

let loadedPromise = null;
function ensureLoaded() {
  if (!loadedPromise) {
    loadedPromise = loadCatalog()
      .then(items => { CATALOG_ITEMS = items; })
      .catch(err => console.error('Erro ao carregar catálogo:', err.message));
  }
  return loadedPromise;
}

// --- cache simples para reduzir chamadas ao oEmbed ---
let cache = { ts: 0, items: [] };
const CACHE_TTL = 1000 * 60;

async function fetchOEmbed(item) {
  const id = item.id;
  try {
    const url = `https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${id}&format=json`;
    const res = await axios.get(url, { timeout: 5000 });
    return {
      id,
      title: item.title || res.data.title,
      author_name: res.data.author_name,
      thumb: item.thumb || res.data.thumbnail_url,
      category: item.category,
      description: item.description,
      featured: item.featured,
      year: item.year || ''
    };
  } catch (err) {
    return {
      id,
      title: item.title || `Vídeo ${id}`,
      author_name: '',
      thumb: item.thumb || `https://img.youtube.com/vi/${id}/hqdefault.jpg`,
      category: item.category,
      description: item.description,
      featured: item.featured,
      year: item.year || ''
    };
  }
}

app.get('/api/health', async (req, res) => {
  const result = {
    ok: true,
    redisConfigured: useRedis,
    nodeEnv: process.env.NODE_ENV || null,
    totalItens: CATALOG_ITEMS.length
  };
  if (useRedis) {
    try {
      await axios.post(`${UPSTASH_URL}/set/tubeflix:health`, 'ok', {
        headers: { Authorization: `Bearer ${UPSTASH_TOKEN}` },
        timeout: 5000
      });
      const r = await axios.get(`${UPSTASH_URL}/get/tubeflix:health`, {
        headers: { Authorization: `Bearer ${UPSTASH_TOKEN}` },
        timeout: 5000
      });
      result.redisWritable = r.data && r.data.result === 'ok';
      result.redisError = null;
    } catch (e) {
      result.redisWritable = false;
      result.redisError = e.response ? `HTTP ${e.response.status} da Upstash` : e.message;
    }
  } else {
    result.redisWritable = false;
  }
  res.json(result);
});

app.get('/api/debug/storage', async (req, res) => {
  const token = process.env.ADMIN_TOKEN;
  const provided = req.get('x-admin-token') || req.query.token;
  if (!token || provided !== token) {
    return res.status(401).json({ error: 'Acesso restrito. Use ?token=SEU_ADMIN_TOKEN' });
  }
  await ensureLoaded();
  let armazenado = null;
  if (useRedis) {
    try {
      const val = await redisGet();
      armazenado = Array.isArray(val) ? val.map(i => ({ id: i.id, title: i.title || '' })) : String(val);
    } catch (e) {
      armazenado = `ERRO AO LER: ${e.message}`;
    }
  }
  res.json({
    redisConfigured: useRedis,
    salvoNoRedis: armazenado === null ? '(chave inexistente)' : armazenado,
    totalSalvoNoRedis: Array.isArray(armazenado) ? armazenado.length : null,
    emMemoriaNestaInstancia: CATALOG_ITEMS.length,
    cacheIdadeSegundos: cache.ts ? Math.round((Date.now() - cache.ts) / 1000) : null
  });
});

// --- endpoints públicos ---
app.get('/api/catalog', async (req, res) => {
  try {
    await ensureLoaded();
    const now = Date.now();
    if (now - cache.ts < CACHE_TTL && cache.items.length) {
      return res.json({ items: cache.items, cached: true });
    }
    const items = await Promise.all(CATALOG_ITEMS.map(fetchOEmbed));
    cache = { ts: now, items };
    res.json({ items, cached: false });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Erro ao montar catálogo' });
  }
});

app.get('/api/ids', async (req, res) => {
  await ensureLoaded();
  res.json({ items: CATALOG_ITEMS });
});

// --- autenticação de admin ---
function requireAdmin(req, res, next) {
  const token = process.env.ADMIN_TOKEN;
  if (token) {
    if (req.get('x-admin-token') === token) return next();
    return res.status(401).json({ error: 'Token de administrador inválido ou ausente' });
  }
  if (IS_PROD) {
    return res.status(401).json({ error: 'ADMIN_TOKEN não configurado no servidor' });
  }
  next(); // ambiente local sem ADMIN_TOKEN: liberado para facilitar o desenvolvimento
}

app.post('/api/catalog/add', requireAdmin, async (req, res) => {
  await ensureLoaded();
  const { id, thumb = '', title = '', category = '', description = '', featured = false, year = '' } = req.body || {};
  if (!YOUTUBE_ID_RE.test(String(id || ''))) {
    return res.status(400).json({ error: 'ID inválido: informe os 11 caracteres do vídeo (letras, números, - ou _)' });
  }
  if (!CATALOG_ITEMS.some(i => i.id === id)) {
    CATALOG_ITEMS.push(normalizeItem({ id, thumb, title, category, description, featured, year }));
    const persisted = await persistCatalog();
    cache.ts = 0;
    return res.json({ ok: true, persisted, items: CATALOG_ITEMS });
  }
  res.json({ ok: true, persisted: true, items: CATALOG_ITEMS });
});

app.post('/api/catalog/remove', requireAdmin, async (req, res) => {
  await ensureLoaded();
  const { id } = req.body || {};
  if (!id) return res.status(400).json({ error: 'id é obrigatório' });
  CATALOG_ITEMS = CATALOG_ITEMS.filter(x => x.id !== id);
  const persisted = await persistCatalog();
  cache.ts = 0;
  res.json({ ok: true, persisted, items: CATALOG_ITEMS });
});

app.post('/api/catalog/update', requireAdmin, async (req, res) => {
  await ensureLoaded();
  const { id, thumb = '', title = '', category = '', description = '', featured = false, year = '' } = req.body || {};
  if (!YOUTUBE_ID_RE.test(String(id || ''))) {
    return res.status(400).json({ error: 'ID inválido: informe os 11 caracteres do vídeo (letras, números, - ou _)' });
  }
  const item = CATALOG_ITEMS.find(i => i.id === id);
  if (!item) return res.status(404).json({ error: 'Vídeo não encontrado no catálogo' });
  const updated = normalizeItem({ id, thumb, title, category, description, featured, year });
  item.thumb = updated.thumb;
  item.title = updated.title;
  item.category = updated.category;
  item.description = updated.description;
  item.featured = updated.featured;
  item.year = updated.year;
  const persisted = await persistCatalog();
  cache.ts = 0;
  res.json({ ok: true, persisted, items: CATALOG_ITEMS });
});

app.post('/api/catalog/import', requireAdmin, async (req, res) => {
  await ensureLoaded();
  const body = req.body || {};
  const list = Array.isArray(body) ? body : body.items;
  if (!Array.isArray(list)) return res.status(400).json({ error: 'Envie um array de vídeos ou { items: [...] }' });
  const seen = new Set();
  const clean = [];
  for (const raw of list) {
    const it = normalizeItem(raw);
    if (!YOUTUBE_ID_RE.test(it.id) || seen.has(it.id)) continue;
    seen.add(it.id);
    clean.push(it);
  }
  if (!clean.length) {
    return res.status(400).json({ error: 'Nenhum vídeo válido encontrado no JSON — catálogo mantido como estava' });
  }
  CATALOG_ITEMS = clean;
  const persisted = await persistCatalog();
  cache.ts = 0;
  res.json({ ok: true, persisted, imported: clean.length, items: CATALOG_ITEMS });
});

// --- servir client estático e SPA fallback ---
const clientPath = path.join(__dirname, '../client');
app.use(express.static(clientPath));

app.get('*', (req, res) => {
  if (req.path.startsWith('/api/')) return res.status(404).json({ error: 'Rota não encontrada' });
  res.sendFile(path.join(clientPath, 'index.html'));
});

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Server rodando na porta ${PORT} (armazenamento: ${useRedis ? 'Redis' : 'arquivo local'})`);
  });
}

module.exports = app;
