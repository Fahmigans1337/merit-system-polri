/* Merit SDM - Web UI bergaya portal Satu SDM (vanilla JS), terhubung ke REST API /api/v1 */
(function () {
  'use strict';
  const API = '/api/v1';
  const $app = document.getElementById('app');

  /* ===================== UTIL ===================== */
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const BULAN = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];
  function fmtDate(d) {
    if (!d) return '-';
    const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(d);
    return m ? `${parseInt(m[3], 10)} ${BULAN[parseInt(m[2], 10) - 1]} ${m[1]}` : d;
  }
  const initials = (s) => (s || '?').split(/[\s.]+/).filter(Boolean).slice(0, 2).map((x) => x[0].toUpperCase()).join('');
  const roleLabel = (r) => (r === 'ADMIN_SSDM' ? 'Admin SSDM' : 'Operator Satker');
  const roleBadge = (r) => `<span class="badge ${r === 'ADMIN_SSDM' ? 'badge-admin' : 'badge-op'}">${roleLabel(r)}</span>`;

  /* ===================== ICONS (inline SVG) ===================== */
  const ICONS = {
    download: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
    bell: '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>',
    user: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    home: '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
    left: '<polyline points="15 18 9 12 15 6"/>',
    right: '<polyline points="9 18 15 12 9 6"/>',
    ext: '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>',
    megaphone: '<path d="M3 11v2a1 1 0 0 0 1 1h3l8 5V5L7 10H4a1 1 0 0 0-1 1z"/><path d="M19 8a5 5 0 0 1 0 8"/>',
    users: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    shield: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    database: '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>',
    code: '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
    search: '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    logout: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>',
    check: '<polyline points="20 6 9 17 4 12"/>',
    list: '<line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><circle cx="3.5" cy="6" r=".6"/><circle cx="3.5" cy="12" r=".6"/><circle cx="3.5" cy="18" r=".6"/>',
    building: '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01M12 6h.01M16 6h.01M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M16 14h.01"/>',
  };
  const ic = (n) => `<svg class="i" viewBox="0 0 24 24" aria-hidden="true">${ICONS[n] || ''}</svg>`;

  /* ===================== PANGKAT ===================== */
  // Urutan pangkat Polri (tertinggi -> terendah)
  const PANGKAT_LIST = [
    { gol: 'Perwira', sub: 'Pati', group: 'Perwira Tinggi (Pati)', items: ['JENDERAL POL', 'KOMJEN POL', 'IRJEN POL', 'BRIGJEN POL'] },
    { gol: 'Perwira', sub: 'Pamen', group: 'Perwira Menengah (Pamen)', items: ['KOMBES POL', 'AKBP', 'KOMPOL'] },
    { gol: 'Perwira', sub: 'Pama', group: 'Perwira Pertama (Pama)', items: ['AKP', 'IPTU', 'IPDA'] },
    { gol: 'Bintara', sub: 'Bintara', group: 'Bintara', items: ['AIPTU', 'AIPDA', 'BRIPKA', 'BRIGADIR', 'BRIPTU', 'BRIPDA'] },
    { gol: 'Tamtama', sub: 'Tamtama', group: 'Tamtama', items: ['ABRIP', 'ABRIPTU', 'ABRIPDA', 'BHARAKA', 'BHARATU', 'BHARADA'] },
  ];
  const pangkatOptions = (sel) => PANGKAT_LIST.map((g) =>
    `<optgroup label="${esc(g.group)}">${g.items.map((x) => `<option value="${x}" ${x === sel ? 'selected' : ''}>${x}</option>`).join('')}</optgroup>`).join('');
  const golonganOf = (pangkat) => PANGKAT_LIST.find((g) => g.items.includes(String(pangkat || '').toUpperCase()));

  /* ===================== BRAND ===================== */
  const EMBLEM = '<img class="emblem" src="/app/img/logo.png" alt="Logo SDM POLRI">';
  const brand = (lg) => `<span class="brand ${lg ? 'lg' : ''}">${EMBLEM}<span class="brand-text"><span class="brand-name">MERIT SDM</span><span class="brand-sub">DIGITAL SYSTEM</span></span></span>`;

  function toast(msg, type) {
    const el = document.createElement('div');
    el.className = 'toast ' + (type || '');
    el.textContent = msg;
    document.getElementById('toasts').appendChild(el);
    setTimeout(() => el.remove(), 4200);
  }

  /* ===================== AUTH STORE ===================== */
  const store = {
    get(k) { return sessionStorage.getItem(k) || localStorage.getItem(k); },
    set(k, v, remember) { (remember ? localStorage : sessionStorage).setItem(k, v); },
    clear() { ['access_token', 'refresh_token'].forEach((k) => { sessionStorage.removeItem(k); localStorage.removeItem(k); }); },
  };
  let ME = null;
  const isAdmin = () => ME && ME.role === 'ADMIN_SSDM';

  /* ===================== API CLIENT ===================== */
  function parseError(data, status) {
    if (!data) return `Terjadi kesalahan (HTTP ${status})`;
    const d = data.detail;
    if (typeof d === 'string') return d;
    if (Array.isArray(d)) {
      return d.map((e) => {
        const field = (e.loc || []).filter((x) => x !== 'body').join('.');
        return (field ? field + ': ' : '') + (e.msg || '').replace('Value error, ', '');
      }).join(' | ');
    }
    return `Terjadi kesalahan (HTTP ${status})`;
  }
  async function rawFetch(method, path, body, token) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers.Authorization = 'Bearer ' + token;
    return fetch(API + path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  }
  async function tryRefresh() {
    const rt = store.get('refresh_token');
    if (!rt) return false;
    const r = await rawFetch('POST', '/auth/refresh', { refresh_token: rt });
    if (!r.ok) return false;
    const t = await r.json();
    const remember = !!localStorage.getItem('refresh_token');
    store.set('access_token', t.access_token, remember);
    store.set('refresh_token', t.refresh_token, remember);
    return true;
  }
  async function api(method, path, body) {
    let res = await rawFetch(method, path, body, store.get('access_token'));
    if (res.status === 401 && path !== '/auth/login') {
      if (await tryRefresh()) res = await rawFetch(method, path, body, store.get('access_token'));
      if (res.status === 401) { logout(true); throw new Error('Sesi berakhir, silakan login kembali'); }
    }
    if (res.status === 204) return null;
    let data = null;
    try { data = await res.json(); } catch (e) { /* no body */ }
    if (!res.ok) throw new Error(parseError(data, res.status));
    return data;
  }

  /* ===================== MODAL ===================== */
  function openModal({ title, body, submitText = 'Simpan', danger = false, onSubmit }) {
    const root = document.getElementById('modal-root');
    root.innerHTML = `<div class="overlay"><div class="modal">
      <div class="modal-head"><h3>${esc(title)}</h3><button type="button" data-close>&times;</button></div>
      <form id="modal-form" novalidate><div class="modal-body"><div id="modal-err"></div>${body}</div>
      <div class="modal-foot"><button type="button" class="btn btn-ghost" data-close>Batal</button>
      <button type="submit" class="btn ${danger ? 'btn-danger' : 'btn-navy'}" id="modal-submit">${esc(submitText)}</button></div></form></div></div>`;
    const close = () => { root.innerHTML = ''; };
    root.querySelectorAll('[data-close]').forEach((b) => b.addEventListener('click', close));
    root.querySelector('.overlay').addEventListener('mousedown', (e) => { if (e.target.classList.contains('overlay')) close(); });
    const form = document.getElementById('modal-form');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = document.getElementById('modal-submit');
      const errBox = document.getElementById('modal-err');
      errBox.innerHTML = '';
      btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>';
      try {
        await onSubmit(Object.fromEntries(new FormData(form).entries()), close);
      } catch (err) {
        errBox.innerHTML = `<div class="err">${esc(err.message)}</div>`;
        btn.disabled = false; btn.textContent = submitText;
      }
    });
  }
  function confirmBox(title, message, onYes, yesText = 'Hapus') {
    openModal({ title, body: `<p>${message}</p>`, submitText: yesText, danger: true, onSubmit: async (_, close) => { await onYes(); close(); } });
  }

  /* ===================== LAYOUT (header saja, seperti Satu SDM) ===================== */
  document.addEventListener('click', () => { const d = document.getElementById('user-dd'); if (d) d.classList.add('hidden'); });

  function layout(inner, crumbs, bare) {
    document.body.classList.add('portal');
    const crumbHtml = crumbs ? `<div class="crumb"><a href="#/" title="Beranda">${ic('home')}</a>${crumbs.map((c) =>
      `<span class="sep">&rsaquo;</span>${c.href ? `<a href="${c.href}">${esc(c.label)}</a>` : `<b>${esc(c.label)}</b>`}`).join('')}</div>` : '';
    $app.innerHTML = `
      <header class="topbar">
        <a href="#/" aria-label="Beranda">${brand()}</a>
        <div class="top-right">
          <a class="icon-btn" href="/openapi.json" target="_blank" title="Unduh spesifikasi OpenAPI">${ic('download')}</a>
          <button class="icon-btn" id="bell-btn" type="button" title="Notifikasi">${ic('bell')}<span class="dot"></span></button>
          <div class="user-menu">
            <button class="user-btn" id="user-btn" type="button" title="Akun">${ic('user')}</button>
            <div class="dropdown hidden" id="user-dd">
              <div class="dd-head"><div class="dd-ava">${esc(initials(ME.username))}</div><div><div class="dd-name">${esc(ME.username)}</div><small style="color:var(--muted)">${esc(ME.email)}</small></div></div>
              <div class="dd-label">Roles</div><div class="dd-role">${esc(roleLabel(ME.role))}</div>
              <button class="dd-item out" id="logout-btn" type="button">${ic('logout')} Keluar</button>
            </div>
          </div>
        </div>
      </header>
      ${bare ? `<main id="view">${inner}</main>` : `<main class="page" id="view">${crumbHtml}<div id="body">${inner}</div></main>`}`;
    document.getElementById('user-btn').addEventListener('click', (e) => { e.stopPropagation(); document.getElementById('user-dd').classList.toggle('hidden'); });
    document.getElementById('user-dd').addEventListener('click', (e) => e.stopPropagation());
    document.getElementById('bell-btn').addEventListener('click', () => toast('Tidak ada notifikasi baru.'));
    document.getElementById('logout-btn').addEventListener('click', () => logout());
  }
  const setBody = (html) => { const b = document.getElementById('body'); if (b) b.innerHTML = html; };
  const loadingHtml = '<div class="loading"><span class="spinner dark"></span> Memuat data...</div>';

  /* ===================== LOGIN ===================== */
  function renderLogin() {
    document.body.classList.remove('portal');
    $app.innerHTML = `<div class="login-wrap"><div class="login-card">
      <div class="login-brand">${brand(true)}</div>
      <h1>Selamat Datang</h1>
      <p class="lead">Silakan masukkan NRP dan kata sandi Anda untuk menggunakan layanan ini.</p>
      <div id="login-err"></div>
      <form id="login-form" novalidate>
        <div class="field field-lg"><input class="input" name="username" autocomplete="username" placeholder="NRP / Username" autofocus></div>
        <div class="field field-lg"><div class="pw-wrap"><input class="input" type="password" name="password" autocomplete="current-password" placeholder="Password"><button type="button" id="pw-toggle">Lihat</button></div></div>
        <div class="row-between"><label class="check"><input type="checkbox" name="remember"> Ingat Saya</label><a href="#" id="forgot">Lupa Password</a></div>
        <button class="btn btn-primary btn-block" id="login-btn" type="submit">Masuk</button>
      </form>
      <div class="demo-box">Akun demo (klik untuk mengisi otomatis)
        <div class="demo-chips">
          <span class="chip" data-u="admin.ssdm" data-p="Admin@12345">Admin SSDM</span>
          <span class="chip" data-u="operator.metro" data-p="Operator@123">Operator Metro</span>
          <span class="chip" data-u="operator.jabar" data-p="Operator@123">Operator Jabar</span>
          <span class="chip" data-u="operator.jatim" data-p="Operator@123">Operator Jatim</span>
          <span class="chip" data-u="operator.sulsel" data-p="Operator@123">Operator Sulsel</span>
        </div></div></div></div>`;
    const form = document.getElementById('login-form');
    document.getElementById('pw-toggle').addEventListener('click', (e) => {
      const i = form.password; i.type = i.type === 'password' ? 'text' : 'password'; e.target.textContent = i.type === 'password' ? 'Lihat' : 'Sembunyikan';
    });
    document.getElementById('forgot').addEventListener('click', (e) => { e.preventDefault(); toast('Hubungi Admin SSDM untuk reset password.'); });
    document.querySelectorAll('.chip').forEach((c) => c.addEventListener('click', () => { form.username.value = c.dataset.u; form.password.value = c.dataset.p; }));
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = document.getElementById('login-btn');
      const box = document.getElementById('login-err');
      const username = form.username.value.trim();
      const password = form.password.value;
      box.innerHTML = '';
      if (!username || !password) { box.innerHTML = '<div class="err">Username dan password wajib diisi.</div>'; return; }
      btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>';
      try {
        const t = await api('POST', '/auth/login', { username, password });
        const remember = form.remember.checked;
        store.set('access_token', t.access_token, remember);
        store.set('refresh_token', t.refresh_token, remember);
        await boot();
      } catch (err) {
        box.innerHTML = `<div class="err">${esc(err.message)}</div>`;
        btn.disabled = false; btn.textContent = 'Masuk';
      }
    });
  }
  function logout(expired) {
    store.clear(); ME = null;
    location.hash = '#/login';
    renderLogin();
    if (expired) toast('Sesi berakhir, silakan login kembali.', 'bad');
  }

  /* ===================== HOME (portal modul) ===================== */
  const MODULES = [
    { label: 'User Management', icon: 'users', href: '#/users', admin: true },
    { label: 'Role Management', icon: 'shield', href: '#/roles', admin: true },
    { label: 'MDM Satker', icon: 'database', href: '#/satker' },
    { label: 'API Management', icon: 'code', href: '/docs', ext: true },
    { label: 'SIPP Personel', icon: 'search', href: '#/sipp' },
  ];
  const NEWS = [
    { t: 'Selamat datang di Merit SDM', d: 'Prototype sistem pengelolaan kualifikasi dan riwayat jabatan personel Polri.', tag: 'Info' },
    { t: 'Riwayat jabatan wajib dilengkapi', d: 'Isi nivelering jabatan, fungsi, dan tanggal mulai (TMT) pada setiap penugasan.', tag: 'Panduan' },
    { t: 'Data dibatasi sesuai satuan kerja', d: 'Operator Satker hanya dapat mengelola personel pada satuan kerjanya sendiri.', tag: 'Akses' },
  ];

  function pageHome() {
    const mods = MODULES.filter((m) => !m.admin || isAdmin());
    const cards = mods.map((m) => `<a class="module" href="${m.href}" ${m.ext ? 'target="_blank"' : ''}><span class="mi">${ic(m.icon)}</span><span class="t">${esc(m.label)}</span></a>`).join('');
    layout(`
      <div class="page" style="padding-bottom:0">
        <section class="hero">
          <h1>SDM UNGGUL POLRI PRESISI.</h1>
          <p>Merit SDM - Satu aplikasi untuk pengelolaan kualifikasi dan riwayat jabatan personel</p>
          <span class="who-line">${esc(ME.username)} &bull; ${esc(roleLabel(ME.role))}</span>
        </section>
        <div class="slider">
          <button class="arrow" id="m-prev" type="button" aria-label="Sebelumnya">${ic('left')}</button>
          <div class="mods" id="mods">${cards}</div>
          <button class="arrow dark" id="m-next" type="button" aria-label="Berikutnya">${ic('right')}</button>
        </div>
        <div class="all-wrap"><button class="btn btn-primary" id="m-all" type="button">Lihat semua modul ${ic('ext')}</button></div>
      </div>
      <div class="panel"><div class="panel-inner">
        <div class="panel-head"><h3>${ic('megaphone')} Pengumuman Terbaru</h3><a class="btn btn-soft btn-sm" href="#/sipp">Lihat lebih banyak ${ic('ext')}</a></div>
        <div class="news">${NEWS.map((n) => `<div class="news-item"><div><b>${esc(n.t)}</b><small>${esc(n.d)}</small></div><span class="tag">${esc(n.tag)}</span></div>`).join('')}</div>
      </div></div>`, null, true);
    const box = document.getElementById('mods');
    document.getElementById('m-prev').addEventListener('click', () => box.scrollBy({ left: -300, behavior: 'smooth' }));
    document.getElementById('m-next').addEventListener('click', () => box.scrollBy({ left: 300, behavior: 'smooth' }));
    document.getElementById('m-all').addEventListener('click', (e) => {
      const all = box.classList.toggle('all');
      e.currentTarget.innerHTML = (all ? 'Ringkas modul ' : 'Lihat semua modul ') + ic('ext');
    });
  }

  /* ===================== SIPP (filter kiri + statistik kanan) ===================== */
  let SATKERS = [];
  async function loadSatkers() { SATKERS = (await api('GET', '/satker?limit=100')).data; return SATKERS; }
  const satkerOptions = (sel, lockToOwn) => SATKERS
    .filter((s) => !lockToOwn || s.id === ME.satker_id)
    .map((s) => `<option value="${s.id}" ${s.id === sel ? 'selected' : ''}>${esc(s.nama)}</option>`).join('');

  const listState = { skip: 0, limit: 10, nama: '', nrp_nip: '', pangkat: '', satker_id: '' };

  function statCard(cls, title, mainLabel, mainVal, subs) {
    return `<div class="sc ${cls}"><div class="sc-title">${esc(title)}</div><div class="sc-row">
      <div class="sc-main"><small>${esc(mainLabel)}</small><b>${mainVal}</b></div>
      ${subs.map((x) => `<div class="sc-sub"><span class="ibox">${ic(x.icon)}</span><div><small>${esc(x.label)}</small><b>${x.val}</b></div></div>`).join('')}
    </div></div>`;
  }

  async function pageSipp() {
    layout(loadingHtml, [{ label: 'SIPP' }, { label: 'Personel' }]);
    await loadSatkers();
    const s = await api('GET', '/dashboard/stats');
    const g = { Perwira: 0, Bintara: 0, Tamtama: 0, Pati: 0, Pamen: 0, Pama: 0 };
    s.per_pangkat.forEach((r) => { const x = golonganOf(r.pangkat); if (x) { g[x.gol] += r.total; if (x.gol === 'Perwira') g[x.sub] += r.total; } });
    const pct = (n) => (s.total_personel ? Math.round((n / s.total_personel) * 100) : 0) + '%';
    const ownSatker = !isAdmin() && s.per_satker[0] ? s.per_satker[0].nama : 'POLRI';
    const polriSubs = [{ icon: 'check', label: 'Jabatan Aktif', val: s.jabatan_aktif }, { icon: 'list', label: 'Riwayat Jabatan', val: s.total_riwayat_jabatan }];
    if (isAdmin()) polriSubs.push({ icon: 'building', label: 'Satuan Kerja', val: s.total_satker });

    setBody(`
      <div class="two">
        <div class="card filter"><h3>Cari Personel</h3>
          ${isAdmin()
            ? `<div class="field"><label>Satuan Kerja</label><select class="select" id="f-satker"><option value="">Semua Satuan Kerja</option>${satkerOptions(listState.satker_id)}</select></div>`
            : `<div class="field"><label>Satuan Kerja</label><input class="input" value="${esc(ownSatker)}" readonly></div>`}
          <div class="field"><label>Nama</label><input class="input" id="f-nama" placeholder="Nama" value="${esc(listState.nama)}"></div>
          <div class="field"><label>NRP</label><input class="input" id="f-nrp" placeholder="NRP" value="${esc(listState.nrp_nip)}"></div>
          <div class="field"><label>Pangkat</label><select class="select" id="f-pangkat"><option value="">Semua Pangkat</option>${pangkatOptions(listState.pangkat)}</select></div>
          <div class="filter-foot"><a id="f-reset">Reset Pencarian</a><button class="btn btn-navy" id="f-go" type="button">Cari Personel</button></div>
        </div>
        <div>
          <div class="stat-stack">
            ${statCard('', ownSatker, 'Total Personel', s.total_personel, polriSubs)}
            ${statCard('red', 'PERWIRA', 'Total Personel', g.Perwira, [{ icon: 'user', label: 'Pati', val: g.Pati }, { icon: 'user', label: 'Pamen', val: g.Pamen }, { icon: 'user', label: 'Pama', val: g.Pama }])}
            ${statCard('blue', 'BINTARA', 'Total Personel', g.Bintara, [{ icon: 'user', label: 'Proporsi', val: pct(g.Bintara) }])}
            ${statCard('orange', 'TAMTAMA', 'Total Personel', g.Tamtama, [{ icon: 'user', label: 'Proporsi', val: pct(g.Tamtama) }])}
          </div>
          <div class="card results"><div class="card-head"><h3>Daftar Personel</h3><button class="btn btn-navy" id="add-p" type="button">Tambah</button></div>
            <div id="plist">${loadingHtml}</div></div>
        </div>
      </div>`);
    document.getElementById('add-p').addEventListener('click', () => personelForm());
    const apply = () => {
      listState.nama = document.getElementById('f-nama').value.trim();
      listState.nrp_nip = document.getElementById('f-nrp').value.trim();
      listState.pangkat = document.getElementById('f-pangkat').value;
      const fs = document.getElementById('f-satker'); listState.satker_id = fs ? fs.value : '';
      listState.skip = 0; refreshList();
    };
    document.getElementById('f-go').addEventListener('click', apply);
    ['f-nama', 'f-nrp'].forEach((id) => document.getElementById(id).addEventListener('keydown', (e) => { if (e.key === 'Enter') apply(); }));
    document.getElementById('f-reset').addEventListener('click', () => { Object.assign(listState, { skip: 0, nama: '', nrp_nip: '', pangkat: '', satker_id: '' }); pageSipp(); });
    refreshList();
  }

  async function refreshList() {
    const box = document.getElementById('plist');
    if (!box) return;
    box.innerHTML = loadingHtml;
    const q = new URLSearchParams({ skip: listState.skip, limit: listState.limit });
    ['nama', 'nrp_nip', 'pangkat', 'satker_id'].forEach((k) => { if (listState[k]) q.set(k, listState[k]); });
    try {
      const r = await api('GET', '/personel?' + q.toString());
      const rows = r.data.length ? r.data.map((p, i) => `
        <tr><td>${listState.skip + i + 1}</td><td><a href="#/sipp/personel/${p.id}"><b>${esc(p.nama)}</b></a></td><td>${esc(p.nrp_nip)}</td>
        <td>${esc(p.pangkat)}</td><td>${esc(p.satker_nama)}</td><td>${esc(p.tempat_lahir)}, ${fmtDate(p.tanggal_lahir)}</td>
        <td><div class="actions"><a class="btn btn-soft btn-sm" href="#/sipp/personel/${p.id}">Detail</a>
        <button class="btn btn-ghost btn-sm" data-edit="${p.id}" type="button">Edit</button>
        <button class="btn btn-danger btn-sm" data-del="${p.id}" data-name="${esc(p.nama)}" type="button">Hapus</button></div></td></tr>`).join('')
        : '<tr><td colspan="7" class="empty">Data tidak ditemukan</td></tr>';
      const page = Math.floor(r.skip / r.limit) + 1;
      box.innerHTML = `<div class="table-wrap"><table><thead><tr><th>No</th><th class="s">Nama</th><th class="s">NRP/NIP</th><th class="s">Pangkat</th><th class="s">Satuan Kerja</th><th>Tempat, Tgl Lahir</th><th>Aksi</th></tr></thead><tbody>${rows}</tbody></table></div>
        <div class="pager"><div>Total ${r.total} personel &bull; Halaman ${page} dari ${Math.max(r.pages, 1)}</div>
        <div class="btns"><button class="btn btn-ghost btn-sm" id="pg-prev" type="button" ${r.skip <= 0 ? 'disabled' : ''}>&lsaquo; Sebelumnya</button>
        <button class="btn btn-ghost btn-sm" id="pg-next" type="button" ${r.skip + r.limit >= r.total ? 'disabled' : ''}>Berikutnya &rsaquo;</button></div></div>`;
      document.getElementById('pg-prev').addEventListener('click', () => { listState.skip = Math.max(0, listState.skip - listState.limit); refreshList(); });
      document.getElementById('pg-next').addEventListener('click', () => { listState.skip += listState.limit; refreshList(); });
      box.querySelectorAll('[data-edit]').forEach((b) => b.addEventListener('click', async () => personelForm(await api('GET', '/personel/' + b.dataset.edit))));
      box.querySelectorAll('[data-del]').forEach((b) => b.addEventListener('click', () =>
        confirmBox('Hapus Personel', `Hapus <b>${esc(b.dataset.name)}</b> beserta seluruh riwayat jabatannya? Tindakan ini tidak dapat dibatalkan.`,
          async () => { await api('DELETE', '/personel/' + b.dataset.del); toast('Personel dihapus', 'ok'); route(); })));
    } catch (err) { box.innerHTML = `<div class="err">${esc(err.message)}</div>`; }
  }

  function personelForm(p) {
    const edit = !!p;
    const lock = !isAdmin();
    openModal({
      title: edit ? 'Edit Personel' : 'Tambah Personel',
      body: `<div class="form-grid">
        <div class="field full"><label>Nama Lengkap *</label><input class="input" name="nama" value="${esc(p?.nama)}"></div>
        <div class="field"><label>NRP / NIP *</label><input class="input" name="nrp_nip" value="${esc(p?.nrp_nip)}" ${edit ? 'readonly' : ''}></div>
        <div class="field"><label>Pangkat *</label><select class="select" name="pangkat"><option value="">-- Pilih Pangkat --</option>${pangkatOptions(p?.pangkat)}</select></div>
        <div class="field"><label>Tempat Lahir *</label><input class="input" name="tempat_lahir" value="${esc(p?.tempat_lahir)}"></div>
        <div class="field"><label>Tanggal Lahir *</label><input class="input" type="date" name="tanggal_lahir" value="${esc(p?.tanggal_lahir)}"></div>
        <div class="field full"><label>Satuan Kerja *</label><select class="select" name="satker_id">${satkerOptions(p?.satker_id || (lock ? ME.satker_id : ''), lock)}</select></div></div>`,
      onSubmit: async (f, close) => {
        const body = { nama: f.nama, pangkat: f.pangkat, tempat_lahir: f.tempat_lahir, tanggal_lahir: f.tanggal_lahir, satker_id: f.satker_id };
        if (!edit) { body.nrp_nip = f.nrp_nip; await api('POST', '/personel', body); toast('Personel ditambahkan', 'ok'); }
        else { await api('PUT', '/personel/' + p.id, body); toast('Personel diperbarui', 'ok'); }
        close(); route();
      },
    });
  }

  /* ===================== DETAIL PERSONEL (sidebar section) ===================== */
  let detailId = null;
  let detailSection = 'pribadi';
  const SECTIONS = [{ k: 'pribadi', label: '1. Data Pribadi' }, { k: 'jabatan', label: '2. Jabatan' }, { k: 'karier', label: '3. Perjalanan Karier' }];

  async function pageDetail(id) {
    layout(loadingHtml, [{ label: 'SIPP', href: '#/sipp' }, { label: 'Personel', href: '#/sipp' }, { label: 'Detail' }]);
    await loadSatkers();
    let p;
    try { p = await api('GET', '/personel/' + id); } catch (err) {
      setBody(`<div class="err">${esc(err.message)}</div><a class="btn btn-ghost" href="#/sipp">&lsaquo; Kembali</a>`); return;
    }
    setBody(`<div class="detail">
      <aside class="side"><h4>Data Personel</h4>${SECTIONS.map((x) => `<a data-sec="${x.k}" class="${x.k === detailSection ? 'active' : ''}">${x.label}</a>`).join('')}</aside>
      <section id="sec"></section></div>`);
    document.querySelectorAll('[data-sec]').forEach((a) => a.addEventListener('click', () => {
      detailSection = a.dataset.sec;
      document.querySelectorAll('[data-sec]').forEach((x) => x.classList.toggle('active', x === a));
      renderSection(p);
    }));
    renderSection(p);
  }

  function renderSection(p) {
    const sec = document.getElementById('sec');
    if (detailSection === 'pribadi') {
      const aktif = p.jabatan_aktif;
      sec.innerHTML = `<div class="card"><div class="card-head"><h3>Data Pribadi</h3>
        <div class="actions"><button class="btn btn-navy" id="ed-p" type="button">Edit</button><button class="btn btn-danger" id="del-p" type="button">Hapus</button></div></div>
        <div class="person-top"><div class="pbig">${esc(initials(p.nama))}</div>
          <div><h2 style="font-size:20px">${esc(p.nama)}</h2><div style="color:var(--muted)">${esc(p.pangkat)} &bull; NRP/NIP ${esc(p.nrp_nip)}</div></div></div>
        <div class="kv"><div><small>Tempat, Tanggal Lahir</small><b>${esc(p.tempat_lahir)}, ${fmtDate(p.tanggal_lahir)}</b></div>
          <div><small>Satuan Kerja</small><b>${esc(p.satker_nama)}</b></div>
          <div><small>Jabatan Saat Ini</small><b>${aktif ? esc(aktif.jabatan) : '-'}</b></div>
          <div><small>Total Riwayat Jabatan</small><b>${p.total_riwayat_jabatan}</b></div></div></div>`;
      document.getElementById('ed-p').addEventListener('click', () => personelForm(p));
      document.getElementById('del-p').addEventListener('click', () => confirmBox('Hapus Personel', `Hapus <b>${esc(p.nama)}</b> beserta seluruh riwayat jabatannya?`,
        async () => { await api('DELETE', '/personel/' + p.id); toast('Personel dihapus', 'ok'); location.hash = '#/sipp'; }));
    } else if (detailSection === 'jabatan') {
      const rows = p.riwayat_jabatan.length ? p.riwayat_jabatan.map((r, i) => `
        <tr><td>${i + 1}</td><td><b>${esc(r.jabatan)}</b></td><td>${esc(r.satuan_kerja)}</td><td>${esc(r.fungsi)}</td><td>${esc(r.nivelering_jabatan)}</td>
        <td>${fmtDate(r.tanggal_mulai)}</td><td>${r.tanggal_berakhir ? fmtDate(r.tanggal_berakhir) : '<i>sekarang</i>'}</td>
        <td><span class="badge ${r.status_jabatan === 'AKTIF' ? 'badge-ok' : 'badge-off'}">${r.status_jabatan === 'AKTIF' ? 'Aktif' : 'Non Aktif'}</span></td>
        <td>${esc(r.keterangan || '-')}</td>
        <td><div class="actions"><button class="btn btn-ghost btn-sm" data-redit="${r.id}" type="button">Edit</button><button class="btn btn-danger btn-sm" data-rdel="${r.id}" type="button">Hapus</button></div></td></tr>`).join('')
        : '<tr><td colspan="10" class="empty">Belum ada riwayat jabatan</td></tr>';
      sec.innerHTML = `<div class="card"><div class="card-head"><h3>Jabatan</h3><button class="btn btn-navy" id="add-rj" type="button">Tambah</button></div>
        <div class="table-wrap"><table><thead><tr><th>No</th><th class="s">Jabatan</th><th class="s">Satuan Kerja</th><th class="s">Fungsi</th><th class="s">Nivelering</th><th class="s">TMT Jabatan</th><th class="s">Berakhir</th><th>Status</th><th>Keterangan</th><th>Aksi</th></tr></thead><tbody>${rows}</tbody></table></div></div>`;
      document.getElementById('add-rj').addEventListener('click', () => jabatanForm(p.id));
      sec.querySelectorAll('[data-redit]').forEach((b) => b.addEventListener('click', () => jabatanForm(p.id, p.riwayat_jabatan.find((x) => x.id === b.dataset.redit))));
      sec.querySelectorAll('[data-rdel]').forEach((b) => b.addEventListener('click', () => confirmBox('Hapus Riwayat Jabatan', 'Hapus riwayat jabatan ini?',
        async () => { await api('DELETE', `/personel/${p.id}/riwayat-jabatan/${b.dataset.rdel}`); toast('Riwayat jabatan dihapus', 'ok'); pageDetail(p.id); })));
    } else {
      const tl = p.riwayat_jabatan.length ? p.riwayat_jabatan.map((r) => `
        <div class="tl-item ${r.status_jabatan === 'AKTIF' ? 'aktif' : ''}"><h4>${esc(r.jabatan)} ${r.status_jabatan === 'AKTIF' ? '<span class="badge badge-ok">Saat ini</span>' : ''}</h4>
        <div class="meta">${esc(r.satuan_kerja)} &bull; ${esc(r.fungsi)} &bull; ${esc(r.nivelering_jabatan)}</div>
        <div class="meta">${fmtDate(r.tanggal_mulai)} &mdash; ${r.tanggal_berakhir ? fmtDate(r.tanggal_berakhir) : 'sekarang'}</div></div>`).join('')
        : '<div class="empty">Belum ada riwayat jabatan</div>';
      sec.innerHTML = `<div class="card"><div class="card-head"><h3>Perjalanan Karier</h3></div><div class="timeline">${tl}</div></div>`;
    }
  }

  function jabatanForm(pid, r) {
    const edit = !!r;
    openModal({
      title: edit ? 'Edit Riwayat Jabatan' : 'Tambah Riwayat Jabatan',
      body: `<div class="form-grid">
        <div class="field full"><label>Jabatan *</label><input class="input" name="jabatan" value="${esc(r?.jabatan)}"></div>
        <div class="field"><label>Satuan Kerja *</label><input class="input" name="satuan_kerja" value="${esc(r?.satuan_kerja)}"></div>
        <div class="field"><label>Fungsi *</label><input class="input" name="fungsi" value="${esc(r?.fungsi)}" placeholder="mis. RESERSE KRIMINAL"></div>
        <div class="field"><label>Nivelering Jabatan *</label><input class="input" name="nivelering_jabatan" value="${esc(r?.nivelering_jabatan)}" placeholder="mis. ES-V/A"></div>
        <div class="field"><label>Status Jabatan *</label><select class="select" name="status_jabatan">
          <option value="AKTIF" ${r?.status_jabatan !== 'NON_AKTIF' ? 'selected' : ''}>Aktif</option><option value="NON_AKTIF" ${r?.status_jabatan === 'NON_AKTIF' ? 'selected' : ''}>Non Aktif</option></select></div>
        <div class="field"><label>Tanggal Mulai (TMT) *</label><input class="input" type="date" name="tanggal_mulai" value="${esc(r?.tanggal_mulai)}"></div>
        <div class="field"><label>Tanggal Berakhir</label><input class="input" type="date" name="tanggal_berakhir" value="${esc(r?.tanggal_berakhir)}"></div>
        <div class="field full"><label>Keterangan</label><textarea class="textarea" name="keterangan" rows="2">${esc(r?.keterangan)}</textarea></div></div>`,
      onSubmit: async (f, close) => {
        const body = { jabatan: f.jabatan, satuan_kerja: f.satuan_kerja, fungsi: f.fungsi, nivelering_jabatan: f.nivelering_jabatan,
          status_jabatan: f.status_jabatan, tanggal_mulai: f.tanggal_mulai || null,
          tanggal_berakhir: f.tanggal_berakhir || null, keterangan: f.keterangan || null };
        if (edit) await api('PUT', `/personel/${pid}/riwayat-jabatan/${r.id}`, body);
        else await api('POST', `/personel/${pid}/riwayat-jabatan`, body);
        toast(edit ? 'Riwayat jabatan diperbarui' : 'Riwayat jabatan ditambahkan', 'ok');
        close(); detailSection = 'jabatan'; pageDetail(pid);
      },
    });
  }

  /* ===================== MDM: SATKER ===================== */
  async function pageSatker() {
    layout(loadingHtml, [{ label: 'MDM' }, { label: 'Satuan Kerja' }]);
    await loadSatkers();
    const rows = SATKERS.length ? SATKERS.map((s, i) => `<tr><td>${i + 1}</td><td><b>${esc(s.nama)}</b></td><td>${esc(s.kode)}</td><td>${esc(s.deskripsi || '-')}</td>
      ${isAdmin() ? `<td><div class="actions"><button class="btn btn-ghost btn-sm" data-sedit="${s.id}" type="button">Edit</button><button class="btn btn-danger btn-sm" data-sdel="${s.id}" data-name="${esc(s.nama)}" type="button">Hapus</button></div></td>` : ''}</tr>`).join('')
      : '<tr><td colspan="5" class="empty">Belum ada satker</td></tr>';
    setBody(`<div class="card"><div class="card-head"><h3>Satuan Kerja</h3>${isAdmin() ? '<button class="btn btn-navy" id="add-s" type="button">Tambah</button>' : ''}</div>
      <div class="table-wrap"><table><thead><tr><th>No</th><th class="s">Nama</th><th class="s">Kode</th><th>Deskripsi</th>${isAdmin() ? '<th>Aksi</th>' : ''}</tr></thead><tbody>${rows}</tbody></table></div></div>`);
    if (!isAdmin()) return;
    document.getElementById('add-s').addEventListener('click', () => satkerForm());
    document.querySelectorAll('[data-sedit]').forEach((b) => b.addEventListener('click', () => satkerForm(SATKERS.find((x) => x.id === b.dataset.sedit))));
    document.querySelectorAll('[data-sdel]').forEach((b) => b.addEventListener('click', () => confirmBox('Hapus Satker', `Hapus satker <b>${esc(b.dataset.name)}</b>? Satker yang masih memiliki personel/pengguna tidak dapat dihapus.`,
      async () => { await api('DELETE', '/satker/' + b.dataset.sdel); toast('Satker dihapus', 'ok'); pageSatker(); })));
  }
  function satkerForm(s) {
    openModal({
      title: s ? 'Edit Satker' : 'Tambah Satker',
      body: `<div class="field"><label>Nama *</label><input class="input" name="nama" value="${esc(s?.nama)}"></div>
        <div class="field"><label>Kode *</label><input class="input" name="kode" value="${esc(s?.kode)}" placeholder="mis. POLDABALI"></div>
        <div class="field"><label>Deskripsi</label><textarea class="textarea" name="deskripsi" rows="2">${esc(s?.deskripsi)}</textarea></div>`,
      onSubmit: async (f, close) => {
        const body = { nama: f.nama, kode: f.kode, deskripsi: f.deskripsi || null };
        if (s) await api('PUT', '/satker/' + s.id, body); else await api('POST', '/satker', body);
        toast(s ? 'Satker diperbarui' : 'Satker ditambahkan', 'ok'); close(); pageSatker();
      },
    });
  }

  /* ===================== ROLE MANAGEMENT (informasi) ===================== */
  function pageRoles() {
    layout('', [{ label: 'Role Management' }]);
    setBody(`<div class="perm">
      <div class="card"><h3>${roleBadge('ADMIN_SSDM')} &nbsp;Admin SSDM</h3><p style="color:var(--muted)">Pengelola pusat dengan akses ke seluruh satuan kerja.</p>
        <ul><li>Kelola seluruh data personel dan riwayat jabatan</li><li>Kelola satuan kerja (MDM)</li><li>Kelola pengguna dan role</li><li>Melihat statistik seluruh satker</li></ul></div>
      <div class="card"><h3>${roleBadge('OPERATOR_SATKER')} &nbsp;Operator Satker</h3><p style="color:var(--muted)">Petugas satuan kerja dengan akses terbatas pada satkernya.</p>
        <ul><li>Kelola personel dan riwayat jabatan di satker sendiri</li><li>Melihat daftar satuan kerja (hanya baca)</li><li>Tidak dapat mengakses manajemen pengguna</li><li>Statistik hanya untuk satker sendiri</li></ul></div></div>`);
  }

  /* ===================== USER MANAGEMENT (ADMIN) ===================== */
  async function pageUsers() {
    layout(loadingHtml, [{ label: 'User Management' }]);
    await loadSatkers();
    const users = await api('GET', '/users?limit=100');
    const sname = (id) => (SATKERS.find((s) => s.id === id) || {}).nama || '-';
    const rows = users.map((u, i) => `<tr><td>${i + 1}</td><td><b>${esc(u.username)}</b></td><td>${esc(u.email)}</td><td>${roleBadge(u.role)}</td><td>${esc(sname(u.satker_id))}</td>
      <td><span class="badge ${u.is_active ? 'badge-ok' : 'badge-off'}">${u.is_active ? 'Aktif' : 'Nonaktif'}</span></td>
      <td><div class="actions"><button class="btn btn-ghost btn-sm" data-uedit="${u.id}" type="button">Edit</button>
      <button class="btn btn-danger btn-sm" data-udel="${u.id}" data-name="${esc(u.username)}" type="button" ${u.id === ME.id ? 'disabled' : ''}>Hapus</button></div></td></tr>`).join('');
    setBody(`<div class="card"><div class="card-head"><h3>User Management</h3><button class="btn btn-navy" id="add-u" type="button">Tambah</button></div>
      <div class="table-wrap"><table><thead><tr><th>No</th><th class="s">Username</th><th class="s">Email</th><th>Role</th><th class="s">Satuan Kerja</th><th>Status</th><th>Aksi</th></tr></thead><tbody>${rows}</tbody></table></div></div>`);
    document.getElementById('add-u').addEventListener('click', () => userForm());
    document.querySelectorAll('[data-uedit]').forEach((b) => b.addEventListener('click', () => userForm(users.find((x) => x.id === b.dataset.uedit))));
    document.querySelectorAll('[data-udel]').forEach((b) => b.addEventListener('click', () => confirmBox('Hapus User', `Hapus pengguna <b>${esc(b.dataset.name)}</b>?`,
      async () => { await api('DELETE', '/users/' + b.dataset.udel); toast('User dihapus', 'ok'); pageUsers(); })));
  }
  function userForm(u) {
    const edit = !!u;
    openModal({
      title: edit ? 'Edit User' : 'Tambah User',
      body: `<div class="form-grid">
        <div class="field"><label>Username *</label><input class="input" name="username" value="${esc(u?.username)}" ${edit ? 'readonly' : ''}></div>
        <div class="field"><label>Email *</label><input class="input" type="email" name="email" value="${esc(u?.email)}"></div>
        <div class="field"><label>Role *</label><select class="select" name="role">
          <option value="OPERATOR_SATKER" ${u?.role !== 'ADMIN_SSDM' ? 'selected' : ''}>Operator Satker</option><option value="ADMIN_SSDM" ${u?.role === 'ADMIN_SSDM' ? 'selected' : ''}>Admin SSDM</option></select></div>
        <div class="field"><label>Satuan Kerja</label><select class="select" name="satker_id"><option value="">- Tidak ada -</option>${satkerOptions(u?.satker_id)}</select></div>
        <div class="field"><label>Password ${edit ? '(kosongkan jika tidak diubah)' : '*'}</label><input class="input" type="password" name="password" placeholder="Minimal 8 karakter" autocomplete="new-password"></div>
        <div class="field"><label>Status</label><select class="select" name="is_active"><option value="true" ${u?.is_active !== false ? 'selected' : ''}>Aktif</option><option value="false" ${u?.is_active === false ? 'selected' : ''}>Nonaktif</option></select></div></div>`,
      onSubmit: async (f, close) => {
        const body = { email: f.email, role: f.role, satker_id: f.satker_id || null, is_active: f.is_active === 'true' };
        if (f.password) body.password = f.password;
        if (edit) await api('PUT', '/users/' + u.id, body);
        else { body.username = f.username; if (!f.password) throw new Error('Password wajib diisi'); await api('POST', '/users', body); }
        toast(edit ? 'User diperbarui' : 'User ditambahkan', 'ok'); close(); pageUsers();
      },
    });
  }

  /* ===================== ROUTER ===================== */
  async function route() {
    if (!ME) return renderLogin();
    const h = location.hash || '#/';
    try {
      if (h === '#/login') { location.hash = '#/'; return; }
      if (h === '#/' || h === '#') return pageHome();
      if (h === '#/sipp') return await pageSipp();
      if (h === '#/personel') { location.hash = '#/sipp'; return; }
      if (h.startsWith('#/personel/')) { location.hash = '#/sipp/personel/' + h.split('/')[2]; return; }
      if (h.startsWith('#/sipp/personel/')) {
        const id = h.split('/')[3];
        if (id !== detailId) { detailId = id; detailSection = 'pribadi'; }
        return await pageDetail(id);
      }
      if (h === '#/satker') return await pageSatker();
      if (h === '#/roles' || h === '#/users') {
        if (!isAdmin()) { toast('Halaman khusus Admin SSDM', 'bad'); location.hash = '#/'; return; }
        return h === '#/roles' ? pageRoles() : await pageUsers();
      }
      location.hash = '#/';
    } catch (err) {
      if (ME) { layout(`<div class="err">${esc(err.message)}</div>`, [{ label: 'Terjadi kesalahan' }]); }
    }
  }

  async function boot() {
    if (!store.get('access_token')) { ME = null; return renderLogin(); }
    try { ME = await api('GET', '/auth/me'); } catch (e) { store.clear(); ME = null; return renderLogin(); }
    if (location.hash === '#/login' || !location.hash) location.hash = '#/';
    route();
  }

  window.addEventListener('hashchange', route);
  boot();
})();
