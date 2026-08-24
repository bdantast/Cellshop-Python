// client/app.js
const API_BASE = window.location.origin;
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[c]));

const row = document.getElementById('row-populares');
const heroTitle = document.getElementById('hero-title');
const heroDesc = document.getElementById('hero-desc');
const heroWatchBtn = document.getElementById('watch-btn');
const heroYoutubeBtn = document.getElementById('hero-youtube');
const heroShareBtn = document.getElementById('hero-share');
const searchInput = document.getElementById('search');
const modal = document.getElementById('player-modal');
const playerContainer = document.getElementById('player-container');
const closeModalBtn = document.getElementById('close-modal');
const chipsEl = document.getElementById('chips');
const menuBtn = document.getElementById('menu-btn');
const menuDropdown = document.getElementById('menu-dropdown');
const catPage = document.getElementById('cat-page');
const catTitle = document.getElementById('cat-title');
const catSub = document.getElementById('cat-sub');
const catGrid = document.getElementById('cat-grid');
const heroSection = document.getElementById('hero');

let ALL_ITEMS = [];
let currentQuery = '';
let activeCategory = '';
const PREVIEW_START = 240; // prévias começam em 4min do vídeo
const HERO_SLIDE_MS = 15000; // quanto tempo cada filme fica no hero

function thumbFor(it) {
  return it.thumb || `https://img.youtube.com/vi/${it.id}/hqdefault.jpg`;
}

function categoriesOf(items) {
  return [...new Set(items.map(i => i.category || 'Diversos'))].sort((a, b) => a.localeCompare(b, 'pt-BR'));
}

function currentCatFromURL() {
  return new URLSearchParams(location.search).get('cat') || '';
}

function openModal(id) {
  if (!playerContainer || !modal) return;
  const it = ALL_ITEMS.find(x => x.id === id);
  const modalTitle = document.getElementById('modal-title');
  if (modalTitle) modalTitle.textContent = it ? (it.title || `Vídeo ${id}`) : `Vídeo ${id}`;
  const openYoutubeBtn = document.getElementById('open-youtube');
  if (openYoutubeBtn) openYoutubeBtn.onclick = () => window.open(`https://www.youtube.com/watch?v=${id}`, '_blank');
  const shareBtn = document.getElementById('share-btn');
  if (shareBtn) shareBtn.onclick = () => shareMovie(id);
  playerContainer.innerHTML = `<iframe src="https://www.youtube.com/embed/${encodeURIComponent(id)}?autoplay=1&rel=0" allow="autoplay; encrypted-media" allowfullscreen title="Player"></iframe>`;
  modal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

async function shareMovie(id) {
  const it = ALL_ITEMS.find(x => x.id === id);
  const title = it ? (it.title || 'Um filme') : 'Um filme';
  const url = `${location.origin}/?v=${encodeURIComponent(id)}`;
  const data = { title: `${title} · TubeFlix`, text: `Assista "${title}" no TubeFlix!`, url };
  try {
    if (navigator.share) {
      await navigator.share(data);
    } else {
      await navigator.clipboard.writeText(url);
      alert('Link copiado! Agora é só colar onde quiser.');
    }
  } catch (err) {
    if (err && err.name === 'AbortError') return;
    prompt('Copie o link do filme:', url);
  }
}

function closeModal() {
  if (!modal || !playerContainer) return;
  modal.classList.add('hidden');
  playerContainer.innerHTML = '';
  document.body.style.overflow = '';
}

closeModalBtn && closeModalBtn.addEventListener('click', closeModal);
modal && modal.addEventListener('click', e => { if (e.target === modal) closeModal(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

// --- hero rotativo com vários destaques ---
let heroTimer = null;
let heroPreviewTimer = null;
let heroIndex = 0;
let heroSlides = [];

function clearHeroPreview() {
  clearTimeout(heroPreviewTimer);
  document.querySelectorAll('#hero-slides .hero-video').forEach(v => {
    v.innerHTML = '';
    v.classList.remove('playing');
  });
}

function showHeroSlide(i) {
  heroIndex = i;
  if (modal && !modal.classList.contains('hidden')) return;
  const it = heroSlides[i];
  if (!it) return;
  const bgs = document.querySelectorAll('#hero-slides .hero-bg');
  bgs.forEach((b, j) => b.classList.toggle('active', j === i));
  document.querySelectorAll('#hero-dots .hero-dot').forEach((d, j) => d.classList.toggle('active', j === i));
  if (heroTitle) heroTitle.textContent = it.title || '';
  if (heroDesc) heroDesc.textContent = [it.description, it.author_name, it.year].filter(Boolean).join(' · ');
  if (heroWatchBtn) heroWatchBtn.onclick = () => openModal(it.id);
  if (heroYoutubeBtn) heroYoutubeBtn.onclick = () => window.open(`https://www.youtube.com/watch?v=${it.id}`, '_blank');
  if (heroShareBtn) heroShareBtn.onclick = () => shareMovie(it.id);

  clearHeroPreview();
  heroPreviewTimer = setTimeout(() => {
    const holder = bgs[i] && bgs[i].querySelector('.hero-video');
    if (!holder || i !== heroIndex) return;
    holder.innerHTML = `<iframe src="https://www.youtube.com/embed/${encodeURIComponent(it.id)}?autoplay=1&mute=1&controls=0&modestbranding=1&rel=0&loop=1&playlist=${encodeURIComponent(it.id)}&playsinline=1&start=${PREVIEW_START}" allow="autoplay; encrypted-media" frameborder="0" tabindex="-1" title="Prévia"></iframe>`;
    const frame = holder.querySelector('iframe');
    frame.addEventListener('load', () => { if (i === heroIndex) holder.classList.add('playing'); });
  }, 1000);
}

function startHeroRotation() {
  clearInterval(heroTimer);
  heroTimer = setInterval(() => {
    if (modal && !modal.classList.contains('hidden')) return;
    showHeroSlide((heroIndex + 1) % heroSlides.length);
  }, HERO_SLIDE_MS);
}

function setupHero(items) {
  const slidesEl = document.getElementById('hero-slides');
  const dotsEl = document.getElementById('hero-dots');
  clearInterval(heroTimer);
  if (!slidesEl || !dotsEl || !items.length) return;
  const pool = items.filter(i => i.featured);
  heroSlides = (pool.length ? pool : items).slice(0, 6);
  slidesEl.innerHTML = heroSlides.map((it, i) =>
    `<div class="hero-bg${i === 0 ? ' active' : ''}"><img src="${esc(thumbFor(it))}" alt="" loading="lazy" onerror='this.onerror=null;this.src="https://img.youtube.com/vi/${encodeURIComponent(it.id)}/hqdefault.jpg"'><div class="hero-video" aria-hidden="true"></div></div>`
  ).join('');
  dotsEl.innerHTML = heroSlides.map((_, i) =>
    `<button class="hero-dot${i === 0 ? ' active' : ''}" aria-label="Destaque ${i + 1}"></button>`
  ).join('');
  heroIndex = 0;
  showHeroSlide(0);
  startHeroRotation();
  dotsEl.onclick = e => {
    const dot = e.target.closest('.hero-dot');
    if (!dot) return;
    showHeroSlide([...dotsEl.children].indexOf(dot));
    startHeroRotation();
  };
}

function skeletonCard() {
  return `
    <div class="card skeleton">
      <div class="sk-thumb"></div>
      <div class="sk-line w80"></div>
      <div class="sk-line w60"></div>
    </div>`;
}

function renderSkeleton() {
  if (!row) return;
  row.innerHTML = `
    <div class="category-section">
      <div class="section-head"><div class="sk-heading"></div></div>
      <div class="row">${skeletonCard().repeat(6)}</div>
    </div>`;
}

function cardHTML(it) {
  return `
    <article class="card" data-open="${esc(it.id)}">
      <div class="thumb-wrap">
        <img class="card-thumb" src="${esc(thumbFor(it))}" alt="${esc(it.title || '')}" loading="lazy" onerror='this.onerror=null;this.src="https://img.youtube.com/vi/${encodeURIComponent(it.id)}/hqdefault.jpg"'>
        <div class="video-preview" aria-hidden="true"></div>
        <span class="play-badge">
          <svg viewBox="0 0 24 24" fill="#fff" aria-hidden="true"><circle cx="12" cy="12" r="11" fill="rgba(229,9,20,.95)"/><path d="M9.5 7.5v9l8-4.5z"/></svg>
        </span>
      </div>
      <div class="card-body">
        <h4 class="card-title">${esc(it.title || '')}</h4>
        <p class="card-author">${esc(it.author_name || '')}${it.year ? ' · ' + esc(it.year) : ''}</p>
        <p class="card-description">${esc(it.description || '')}</p>
        <button class="watch" data-open="${esc(it.id)}">Assistir</button>
      </div>
      <div class="card-hover-overlay">
        <h4 class="hp-title">${esc(it.title || '')}</h4>
        <p class="hp-author">${esc(it.author_name || '')}${it.year ? ' · ' + esc(it.year) : ''}</p>
        <p class="hp-desc">${esc(it.description || 'Sem descrição.')}</p>
        <a class="hp-cat" href="./?cat=${encodeURIComponent(it.category || 'Diversos')}">${esc(it.category || 'Diversos')}</a>
        <div class="hp-actions">
          <button class="watch hp-watch" data-open="${esc(it.id)}">Assistir</button>
          <button class="hp-share" data-share="${esc(it.id)}">Compartilhar</button>
          <a class="hp-yt" href="https://www.youtube.com/watch?v=${encodeURIComponent(it.id)}" target="_blank" rel="noopener">YouTube ↗</a>
        </div>
      </div>
    </article>`;
}

function sectionHTML(cat, videos) {
  return `
    <div class="category-section">
      <div class="section-head">
        <h3><a class="sec-link" href="./?cat=${encodeURIComponent(cat)}">${esc(cat)}</a></h3>
        <span class="section-count">${videos.length} ${videos.length === 1 ? 'vídeo' : 'vídeos'}</span>
      </div>
      <button class="row-nav prev" aria-label="Voltar">‹</button>
      <button class="row-nav next" aria-label="Avançar">›</button>
      <div class="row">${videos.map(cardHTML).join('')}</div>
    </div>`;
}

function renderCatalog(items, query) {
  if (!row) return;

  if (!ALL_ITEMS.length) {
    row.innerHTML = `<div class="empty-state">Catálogo vazio. Adicione vídeos pela <a href="./admin.html">página de admin</a>.</div>`;
    return;
  }
  if (query && !items.length) {
    row.innerHTML = `<div class="empty-state">Nenhum resultado para <strong>"${esc(query)}"</strong>.</div>`;
    return;
  }
  if (!query && !items.length && activeCategory) {
    row.innerHTML = `<div class="empty-state">Nenhum vídeo nesta categoria ainda.</div>`;
    return;
  }

  const categories = {};
  items.forEach(it => {
    const cat = it.category || 'Diversos';
    (categories[cat] = categories[cat] || []).push(it);
  });
  const sortedCats = Object.keys(categories).sort((a, b) => {
    if (a === 'Diversos') return 1;
    if (b === 'Diversos') return -1;
    return a.localeCompare(b, 'pt-BR');
  });

  let html = '';
  if (!activeCategory && !query && ALL_ITEMS.length >= 4) {
    html += sectionHTML('Adicionados recentemente', [...ALL_ITEMS].slice(-8).reverse());
  }
  html += sortedCats.map(cat => sectionHTML(cat, categories[cat])).join('');
  row.innerHTML = html;
  wireHoverPreviews();
}

// --- preview de vídeo ao passar o mouse ---
function wireHoverPreviews(scopeEl) {
  if (!window.matchMedia('(hover: hover)').matches) return;
  const root = scopeEl || row;
  root.querySelectorAll('.card').forEach(card => {
    const holder = card.querySelector('.video-preview');
    if (!holder) return;
    let timer;
    card.addEventListener('mouseenter', () => {
      timer = setTimeout(() => {
        const id = card.dataset.open;
        holder.innerHTML = `<iframe src="https://www.youtube.com/embed/${encodeURIComponent(id)}?autoplay=1&mute=1&controls=0&modestbranding=1&rel=0&loop=1&playlist=${encodeURIComponent(id)}&playsinline=1&start=${PREVIEW_START}" allow="autoplay; encrypted-media" frameborder="0" tabindex="-1" title="Prévia"></iframe>`;
      }, 800);
    });
    card.addEventListener('mouseleave', () => {
      clearTimeout(timer);
      holder.innerHTML = '';
    });
  });
}

function wireCardActions(rootEl) {
  rootEl && rootEl.addEventListener('click', e => {
    const nav = e.target.closest('.row-nav');
    if (nav) {
      const scroller = nav.closest('.category-section').querySelector('.row');
      const dir = nav.classList.contains('prev') ? -1 : 1;
      scroller.scrollBy({ left: dir * scroller.clientWidth * 0.85, behavior: 'smooth' });
      return;
    }
    if (e.target.closest('a')) return;
    const shareEl = e.target.closest('[data-share]');
    if (shareEl) { shareMovie(shareEl.dataset.share); return; }
    const openEl = e.target.closest('[data-open]');
    if (openEl) openModal(openEl.dataset.open);
  });
}
wireCardActions(row);
wireCardActions(catGrid);

searchInput && searchInput.addEventListener('input', () => {
  currentQuery = searchInput.value.trim().toLowerCase();
  applyFilter();
});

function applyFilter() {
  let list = ALL_ITEMS;
  if (activeCategory) list = list.filter(it => (it.category || 'Diversos') === activeCategory);
  if (currentQuery) {
    list = list.filter(it =>
      [it.title, it.author_name, it.category, it.description]
        .some(v => String(v || '').toLowerCase().includes(currentQuery))
    );
    return renderCatalog(list, currentQuery);
  }
  renderCatalog(list);
}

// --- chips de filtro por categoria ---
function buildChips() {
  if (!chipsEl) return;
  const cats = categoriesOf(ALL_ITEMS);
  chipsEl.innerHTML = ['Todos', ...cats].map(c => {
    const val = c === 'Todos' ? '' : c;
    return `<button class="chip${val === activeCategory ? ' active' : ''}" data-cat="${esc(val)}">${esc(c)}</button>`;
  }).join('');
}
chipsEl && chipsEl.addEventListener('click', e => {
  const chip = e.target.closest('.chip');
  if (!chip) return;
  activeCategory = chip.dataset.cat || '';
  buildChips();
  applyFilter();
});

// --- menu Categorias no topo direito ---
function buildMenu() {
  if (!menuDropdown) return;
  const cats = categoriesOf(ALL_ITEMS);
  menuDropdown.innerHTML = cats.length
    ? cats.map(c => `<a href="./?cat=${encodeURIComponent(c)}">${esc(c)}</a>`).join('')
    : '<span class="menu-empty">Sem categorias ainda</span>';
}
function closeMenu() {
  menuDropdown && menuDropdown.classList.add('hidden');
  menuBtn && menuBtn.setAttribute('aria-expanded', 'false');
}
menuBtn && menuBtn.addEventListener('click', e => {
  e.stopPropagation();
  if (!menuDropdown) return;
  const hidden = menuDropdown.classList.toggle('hidden');
  menuBtn.setAttribute('aria-expanded', String(!hidden));
});
document.addEventListener('click', e => {
  if (menuDropdown && !menuDropdown.classList.contains('hidden') && !e.target.closest('.menu')) closeMenu();
});
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(); });

// --- página de categoria (?cat=Nome) ---
function renderCategoryPage(cat) {
  if (!catPage || !catGrid) return;
  const items = ALL_ITEMS.filter(it => (it.category || 'Diversos') === cat);
  document.title = `${cat} · TubeFlix`;
  if (catTitle) catTitle.textContent = cat;
  if (catSub) catSub.textContent = items.length
    ? `${items.length} ${items.length === 1 ? 'vídeo' : 'vídeos'} nesta categoria`
    : 'Nenhum vídeo nesta categoria ainda.';
  catGrid.innerHTML = items.map(cardHTML).join('');
  wireHoverPreviews(catGrid);
  heroSection && heroSection.classList.add('hidden');
  chipsEl && chipsEl.classList.add('hidden');
  row && row.classList.add('hidden');
  catPage.classList.remove('hidden');
}

function renderHome() {
  document.title = 'TubeFlix';
  heroSection && heroSection.classList.remove('hidden');
  chipsEl && chipsEl.classList.remove('hidden');
  row && row.classList.remove('hidden');
  catPage && catPage.classList.add('hidden');
  if (catGrid) catGrid.innerHTML = '';
}

function route() {
  const cat = currentCatFromURL();
  if (cat && ALL_ITEMS.length && categoriesOf(ALL_ITEMS).includes(cat)) renderCategoryPage(cat);
  else { renderHome(); renderCatalog(ALL_ITEMS); }
}
window.addEventListener('popstate', route);

async function loadCatalog() {
  try {
    const res = await fetch(`${API_BASE}/api/catalog`, { cache: 'no-store' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    ALL_ITEMS = data.items || [];
    buildChips();
    buildMenu();
    route();
    if (!currentCatFromURL()) setupHero(ALL_ITEMS);
    const vid = new URLSearchParams(location.search).get('v');
    if (vid && ALL_ITEMS.some(i => i.id === vid)) openModal(vid);
  } catch (err) {
    console.error('Erro ao carregar catálogo', err);
    if (row) row.innerHTML = '<p class="empty-state">Erro ao carregar o catálogo. Tente recarregar a página.</p>';
  }
}

renderSkeleton();
window.addEventListener('load', () => loadCatalog());
window.__app = { loadCatalog, openModal, closeModal };
