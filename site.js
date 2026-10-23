// Portfolio behaviour: featured, the vault (swaps one tile at a time), the index,
// the project panel and the zoom/pan viewer. The content lives in data.js.
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const byId = Object.fromEntries(PROJECTS.map(p => [p.id, p]));
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  // ── tiles ──
  // Videos play (muted) whenever they're on screen. Tiles with several pieces
  // show each one in turn: a picture for 5 s, a video until it has played through.
  const playIO = new IntersectionObserver(entries => {
    for (const e of entries) {
      if (e.isIntersecting) { e.target.preload = 'auto'; e.target.play().catch(() => {}); }
      else e.target.pause();
    }
  }, { threshold: 0.2 });
  const shown = new Set();
  const showIO = new IntersectionObserver(entries => {
    for (const e of entries) e.isIntersecting ? shown.add(e.target) : shown.delete(e.target);
  });

  function media(item, { play = true } = {}) {
    if (item.type === 'video' && play) {
      return `<video src="${esc(item.src)}" poster="${esc(item.thumb)}" muted loop playsinline preload="none"></video>`;
    }
    return `<img src="${esc(item.thumb)}" alt="" loading="lazy" decoding="async">`;
  }

  function tile(p, { line = false, single = false } = {}) {
    const el = document.createElement('button');
    el.className = 'tile';
    el.dataset.id = p.id;
    const many = p.items.length > 1 && !single;
    el.innerHTML = `
      <div class="tile__media">${many ? p.items.map((it, i) => (it.type === 'video'
          ? `<video src="${esc(it.src)}" poster="${esc(it.thumb)}" muted playsinline preload="none" class="slide${i ? '' : ' on'}"></video>`
          : `<img src="${esc(it.thumb)}" alt="" loading="lazy" decoding="async" class="slide${i ? '' : ' on'}">`)).join('')
        : media(p.items[0])}
        ${many ? `<span class="tile__count"><b>1</b> / ${p.items.length}</span>` : ''}
      </div>
      <div class="tile__meta"><span class="tile__title">${esc(p.title)}</span><span class="tile__cat">${esc(p.cat)}</span></div>
      ${line ? `<p class="featured__line">${esc(p.line)}</p>` : ''}`;
    el.setAttribute('aria-label', `${p.title}, ${p.cat}. Open details`);
    el.addEventListener('click', () => openPanel(p));
    if (many) { el._at = 0; el._t = 0; showIO.observe(el); observeSlides(el); }
    else el.querySelectorAll('video').forEach(v => playIO.observe(v));
    return el;
  }

  const IMAGE_MS = 5000, MIN_MS = 4000, STEP = 250;
  const showSlide = (el, i) => {
    const slides = el.querySelectorAll('.slide');
    const old = slides[el._at];
    old.classList.remove('on');
    if (old.tagName === 'VIDEO') { old.pause(); old.currentTime = 0; }
    el._at = i; el._t = 0;
    slides[i].classList.add('on');
    if (slides[i].tagName === 'VIDEO') { slides[i].preload = 'auto'; slides[i].play().catch(() => {}); }
    el.querySelector('.tile__count b').textContent = i + 1;
  };
  setInterval(() => {
    for (const el of shown) {
      if (!el.isConnected) { shown.delete(el); continue; }
      const slides = el.querySelectorAll('.slide'), cur = slides[el._at];
      el._t += STEP;
      let done;
      if (cur.tagName === 'VIDEO') {
        if (cur.paused && !cur.ended) { cur.preload = 'auto'; cur.play().catch(() => {}); }
        if (cur.ended && el._t < MIN_MS) { cur.currentTime = 0; cur.play().catch(() => {}); }   // short clip: play it again
        done = (cur.ended && el._t >= MIN_MS) || cur.error || el._t > 120000;
      } else done = el._t >= IMAGE_MS;
      if (done) showSlide(el, (el._at + 1) % slides.length);
    }
  }, STEP);
  // off screen: stop the clip that's showing
  const pauseOff = new IntersectionObserver(entries => {
    for (const e of entries) if (!e.isIntersecting) e.target.querySelectorAll('video.slide').forEach(v => v.pause());
  });
  const observeSlides = el => pauseOff.observe(el);

  // ── featured: the lead shows its video if it has one, the others flick through ──
  const featured = $('#featured');
  FEATURED.forEach((id, i) => {
    const p = byId[id];
    const t = tile(p, { line: i === 0, single: p.items[0].type === 'video' });
    t.classList.add(`featured__${i}`);
    featured.append(t);
  });

  // ── vault ──
  const vault = $('#vaultGrid'), bar = $('#vaultBar'), pauseBtn = $('#vaultPause');
  const SWAP_MS = 9000;      // slow enough to take a piece in
  const pool = PROJECTS.filter(p => !FEATURED.includes(p.id));
  let slots = [], queue = [], elapsed = 0, last = performance.now();
  let userPaused = false, hovered = false, onScreen = false;

  const shuffle = a => { for (let i = a.length - 1; i > 0; i--) { const j = Math.random() * (i + 1) | 0; [a[i], a[j]] = [a[j], a[i]]; } return a; };

  function slotCount() {
    const cols = getComputedStyle(vault).gridTemplateColumns.split(' ').length || 4;
    return cols * 2;                                      // always two rows
  }

  // add or drop slots to match the columns; the tiles already showing stay put
  function fillVault() {
    const n = slotCount();
    if (!queue.length && !slots.length) queue = shuffle(pool.slice());
    while (slots.length > n) { queue.push(slots.pop()); vault.lastElementChild.remove(); }
    while (slots.length < n) {
      if (!queue.length) queue = shuffle(pool.filter(p => !slots.includes(p)));
      const p = queue.shift();
      slots.push(p); vault.append(tile(p));
    }
    $('#vaultCount').textContent = `${pool.length} projects`;
  }

  function swapOne() {
    if (!queue.length) queue = shuffle(pool.filter(p => !slots.includes(p)));
    const next = queue.shift();
    const k = Math.random() * slots.length | 0;
    const old = vault.children[k];
    if (!old || old.classList.contains('is-active')) return;  // never swap what's open in the panel
    slots[k] = next;
    const box = old.querySelector('.tile__media');
    box.classList.add('leaving');
    setTimeout(() => old.replaceWith(tile(next)), 600);
  }

  function tick(now) {
    const dt = now - last; last = now;
    const running = !userPaused && !hovered && onScreen && !document.hidden && !viewer.open;
    if (running) {
      elapsed += dt;
      if (elapsed >= SWAP_MS) { elapsed = 0; swapOne(); }
    }
    bar.style.width = `${(elapsed / SWAP_MS) * 100}%`;
    requestAnimationFrame(tick);
  }

  vault.addEventListener('pointerenter', () => hovered = true);
  vault.addEventListener('pointerleave', () => hovered = false);
  pauseBtn.addEventListener('click', () => {
    userPaused = !userPaused;
    pauseBtn.setAttribute('aria-pressed', userPaused);
    pauseBtn.textContent = userPaused ? 'Play' : 'Pause';
  });
  new IntersectionObserver(([e]) => onScreen = e.isIntersecting).observe(vault);

  // ── index ──
  const indexGrid = $('#indexGrid'), filters = $('#filters');
  const cats = ['All', ...new Set(PROJECTS.map(p => p.cat))];
  PROJECTS.forEach(p => indexGrid.append(tile(p)));
  cats.forEach(c => {
    const b = document.createElement('button');
    b.className = 'chip'; b.textContent = c; b.setAttribute('role', 'tab');
    b.setAttribute('aria-selected', c === 'All');
    b.addEventListener('click', () => {
      filters.querySelectorAll('.chip').forEach(x => x.setAttribute('aria-selected', x === b));
      indexGrid.querySelectorAll('.tile').forEach(t => t.hidden = c !== 'All' && byId[t.dataset.id].cat !== c);
    });
    filters.append(b);
  });

  // ── panel ──
  const panel = $('#panel'), panelBody = $('#panelBody');
  let panelProject = null;

  function openPanel(p) {
    panelProject = p;
    document.querySelectorAll('.tile.is-active').forEach(t => t.classList.remove('is-active'));
    document.querySelectorAll(`.tile[data-id="${p.id}"]`).forEach(t => t.classList.add('is-active'));
    $('#panelCount').textContent = `${String(PROJECTS.indexOf(p) + 1).padStart(2, '0')} / ${PROJECTS.length}`;
    panelBody.innerHTML = `
      <h3>${esc(p.title)}</h3>
      <p class="panel__line">${esc(p.line)}</p>
      ${p.story ? `<p class="panel__story">${esc(p.story)}</p>` : ''}
      <dl class="panel__facts">
        <dt>Type</dt><dd>${esc(p.cat)}</dd>
        <dt>Tools</dt><dd>${esc(p.tools)}</dd>
        <dt>Year</dt><dd>${p.year}</dd>
        <dt>Pieces</dt><dd>${p.items.length}</dd>
      </dl>
      <div class="panel__items">${p.items.map((it, i) => `
        <button class="tile" data-i="${i}" aria-label="View piece ${i + 1} fullscreen">
          <div class="tile__media">${media(it)}</div>
        </button>`).join('')}
      </div>
      <p class="panel__hint">Click any piece to view it fullscreen.</p>`;
    panelBody.scrollTop = 0;
    panelBody.querySelectorAll('video').forEach(v => playIO.observe(v));
    panelBody.querySelectorAll('[data-i]').forEach(b => b.addEventListener('click', () => openViewer(p.items, +b.dataset.i, p)));
    document.body.classList.add('panel-open');
    panel.setAttribute('aria-hidden', 'false');
    // the grids reflow into the space that's left; refit the vault once they have
    setTimeout(() => { fillVault(); markActive(); }, 480);
  }

  function markActive() {
    if (!panelProject) return;
    document.querySelectorAll(`.tile[data-id="${panelProject.id}"]`).forEach(t => t.classList.add('is-active'));
  }

  function closePanel() {
    document.body.classList.remove('panel-open');
    panel.setAttribute('aria-hidden', 'true');
    document.querySelectorAll('.tile.is-active').forEach(t => t.classList.remove('is-active'));
    panelProject = null;
    setTimeout(fillVault, 480);
  }
  $('#panelClose').addEventListener('click', closePanel);

  // ── viewer: zoom + pan ──
  const viewer = { open: false, items: [], i: 0, project: null, s: 1, x: 0, y: 0, w: 0, h: 0 };
  const vEl = $('#viewer'), stage = $('#stage'), stageMedia = $('#stageMedia'), zoomLbl = $('#vReset');
  const MIN = 1, MAX = 8;

  function openViewer(items, i, project) {
    Object.assign(viewer, { open: true, items, i, project });
    vEl.classList.add('open'); vEl.setAttribute('aria-hidden', 'false');
    document.body.classList.add('viewer-open');
    show();
  }

  function closeViewer() {
    viewer.open = false;
    vEl.classList.remove('open'); vEl.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('viewer-open');
    stageMedia.querySelector('video')?.pause();
    setTimeout(() => { if (!viewer.open) stageMedia.innerHTML = ''; }, 300);
  }

  function fit() {
    const it = viewer.items[viewer.i], pad = 48;
    const k = Math.min((innerWidth - pad * 2) / it.w, (innerHeight - pad * 2 - 56) / it.h, 1.5);
    viewer.w = it.w * k; viewer.h = it.h * k;
    stageMedia.style.width = `${viewer.w}px`;
    stageMedia.style.height = `${viewer.h}px`;
  }

  function show() {
    const it = viewer.items[viewer.i];
    stageMedia.innerHTML = it.type === 'video'
      ? `<video src="${esc(it.src)}" poster="${esc(it.thumb)}" autoplay loop playsinline controls></video>`
      : `<img src="${esc(it.thumb)}" alt="">`;
    if (it.type === 'image') {                      // thumb first, full size once it's in
      const full = new Image();
      full.onload = () => { const img = stageMedia.querySelector('img'); if (img && viewer.items[viewer.i] === it) img.src = it.src; };
      full.src = it.src;
    }
    const p = viewer.project;
    $('#viewerCaption').innerHTML = p ? `<b>${esc(p.title)}</b><span class="mono">${viewer.i + 1} / ${viewer.items.length}</span>` : '';
    $('#vPrev').disabled = $('#vNext').disabled = viewer.items.length < 2;
    fit(); reset();
  }

  function apply() {
    // keep at least a third of the picture on screen
    const mx = Math.max(0, (viewer.w * viewer.s) / 2 - innerWidth / 6);
    const my = Math.max(0, (viewer.h * viewer.s) / 2 - innerHeight / 6);
    if (viewer.s === 1) { viewer.x = viewer.y = 0; }
    viewer.x = Math.max(-mx, Math.min(mx, viewer.x));
    viewer.y = Math.max(-my, Math.min(my, viewer.y));
    stageMedia.style.transform =
      `translate(${viewer.x - (viewer.w * viewer.s) / 2}px, ${viewer.y - (viewer.h * viewer.s) / 2}px) scale(${viewer.s})`;
    zoomLbl.textContent = `${Math.round(viewer.s * 100)}%`;
    const v = stageMedia.querySelector('video');
    if (v) v.controls = viewer.s === 1;             // zoomed in, a drag pans instead
  }

  function reset() { viewer.s = 1; viewer.x = viewer.y = 0; stageMedia.style.transition = 'transform .3s'; apply(); }

  // zoom so the point under (cx, cy) stays put
  function zoomAt(s, cx = innerWidth / 2, cy = innerHeight / 2, smooth = false) {
    s = Math.max(MIN, Math.min(MAX, s));
    const px = cx - innerWidth / 2, py = cy - innerHeight / 2;
    viewer.x = px - (px - viewer.x) * (s / viewer.s);
    viewer.y = py - (py - viewer.y) * (s / viewer.s);
    viewer.s = s;
    stageMedia.style.transition = smooth ? 'transform .25s' : 'none';
    apply();
  }

  stage.addEventListener('wheel', e => {
    e.preventDefault();
    zoomAt(viewer.s * Math.exp(-e.deltaY * 0.0015), e.clientX, e.clientY);
  }, { passive: false });

  stage.addEventListener('dblclick', e => zoomAt(viewer.s > 1 ? 1 : 2.5, e.clientX, e.clientY, true));

  // drag to pan, two fingers to pinch
  const ptrs = new Map();
  let pinch = null, moved = false;
  stage.addEventListener('pointerdown', e => {
    if (e.target.tagName === 'VIDEO' && viewer.s === 1) return;    // let the video controls work
    stage.setPointerCapture(e.pointerId);
    ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    moved = false;
    if (ptrs.size === 2) {
      const [a, b] = [...ptrs.values()];
      pinch = { d: Math.hypot(a.x - b.x, a.y - b.y), s: viewer.s };
    }
    stage.classList.add('dragging');
    stageMedia.style.transition = 'none';
  });
  stage.addEventListener('pointermove', e => {
    const prev = ptrs.get(e.pointerId);
    if (!prev) return;
    const cur = { x: e.clientX, y: e.clientY };
    ptrs.set(e.pointerId, cur);
    if (ptrs.size === 2 && pinch) {
      const [a, b] = [...ptrs.values()];
      zoomAt(pinch.s * Math.hypot(a.x - b.x, a.y - b.y) / pinch.d, (a.x + b.x) / 2, (a.y + b.y) / 2);
    } else if (viewer.s > 1) {
      viewer.x += cur.x - prev.x; viewer.y += cur.y - prev.y;
      apply();
    }
    if (Math.abs(cur.x - prev.x) + Math.abs(cur.y - prev.y) > 2) moved = true;
  });
  const up = e => {
    ptrs.delete(e.pointerId);
    if (ptrs.size < 2) pinch = null;
    if (!ptrs.size) stage.classList.remove('dragging');
  };
  stage.addEventListener('pointerup', e => {
    up(e);
    // a plain click on the dark backdrop closes, like most viewers
    if (!moved && e.target === stage && viewer.s === 1) closeViewer();
  });
  stage.addEventListener('pointercancel', up);

  const step = d => { viewer.i = (viewer.i + d + viewer.items.length) % viewer.items.length; show(); };
  $('#vPrev').addEventListener('click', () => step(-1));
  $('#vNext').addEventListener('click', () => step(1));
  $('#vIn').addEventListener('click', () => zoomAt(viewer.s * 1.5, undefined, undefined, true));
  $('#vOut').addEventListener('click', () => zoomAt(viewer.s / 1.5, undefined, undefined, true));
  $('#vReset').addEventListener('click', reset);
  $('#vClose').addEventListener('click', closeViewer);

  addEventListener('keydown', e => {
    if (viewer.open) {
      if (e.key === 'Escape') closeViewer();
      else if (e.key === 'ArrowRight') step(1);
      else if (e.key === 'ArrowLeft') step(-1);
      else if (e.key === '+' || e.key === '=') zoomAt(viewer.s * 1.5, undefined, undefined, true);
      else if (e.key === '-') zoomAt(viewer.s / 1.5, undefined, undefined, true);
      else if (e.key === '0') reset();
    } else if (e.key === 'Escape' && panelProject) closePanel();
  });

  // ── page ──
  let resizeT;
  addEventListener('resize', () => {
    clearTimeout(resizeT);
    resizeT = setTimeout(() => { fillVault(); markActive(); if (viewer.open) { fit(); apply(); } }, 150);
  });

  const nav = $('.nav');
  addEventListener('scroll', () => nav.classList.toggle('scrolled', scrollY > 10), { passive: true });

  const music = $('#music'), audio = $('#bgMusic');
  music.addEventListener('click', () => {
    const on = audio.paused;
    on ? audio.play().catch(() => {}) : audio.pause();
    music.setAttribute('aria-pressed', on);
  });

  fillVault();
  requestAnimationFrame(tick);
})();
