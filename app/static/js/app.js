/* Merit System Personel - Web UI (vanilla JS), terhubung ke REST API /api/v1 */
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

  const EMBLEM = `<svg class="emblem" viewBox="0 0 74 84" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <path d="M37 2 70 14v30c0 20-14 33-33 38C18 77 4 64 4 44V14z" fill="#f5c518" stroke="#0b2a63" stroke-width="3"/>
    <circle cx="37" cy="40" r="17" fill="#0b2a63"/><path d="M37 26l4 9h9l-7 6 3 9-9-5-9 5 3-9-7-6h9z" fill="#f5c518"/></svg>`;

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
  function openModal({ title, body, submitText = 'Simpan', danger = false, onSubmit, hideFooter = false }) {
    const root = document.getElementById('modal-root');
    root.innerHTML = `<div class="overlay"><div class="modal">
      <div class="modal-head"><h3>${esc(title)}</h3><button type="button" data-close>&times;</button></div>
      <form id="modal-form" novalidate><div class="modal-body"><div id="modal-err"></div>${body}</div>
      ${hideFooter ? '' : `<div class="modal-foot"><button type="button" class="btn btn-ghost" data-close>Batal</button>
      <button type="submit" class="btn ${danger ? 'btn-danger' : 'btn-primary'}" id="modal-submit">${esc(submitText)}</button></div>`}</form></div></div>`;
    const close = () => { root.innerHTML = ''; };
    root.querySelectorAll('[data-close]').forEach((b) => b.addEventListener('click', close));
    root.querySelector('.overlay').addEventListener('mousedown', (e) => { if (e.target.classList.contains('overlay')) close(); });
    const form = document.getElementById('modal-form');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = document.getElementById('modal-submit');
      const errBox = document.getElementById('modal-err');
      errBox.innerHTML = '';
      if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>'; }
      try {
        const fd = Object.fromEntries(new FormData(form).entries());
        await onSubmit(fd, close);
      } catch (err) {
        errBox.innerHTML = `<div class="err">${esc(err.message)}</div>`;
        if (btn) { btn.disabled = false; btn.textContent = submitText; }
      }
    });
    return close;
  }

  function confirmBox(title, message, onYes, yesText = 'Hapus') {
    openModal({ title, body: `<p>${message}</p>`, submitText: yesText, danger: true, onSubmit: async (_, close) => { await onYes(); close(); } });
  }

  /* ===================== LAYOUT ===================== */
  const NAV = [
    { href: '#/', icon: '🏠', label: 'Dashboard', admin: false },
    { href: '#/personel', icon: '👮', label: 'Personel', admin: false },
    { href: '#/satker', icon: '🏢', label: 'Satuan Kerja', admin: false },
    { href: '#/users', icon: '👥', label: 'Manajemen User', admin: true },
  ];

  function layout(activeHref, inner) {
    const items = NAV.filter((n) => !n.admin || isAdmin()).map((n) =>
      `<a href="${n.href}" class="${n.href === activeHref ? 'active' : ''}"><span class="ic">${n.icon}</span>${n.label}</a>`).join('');
    $app.innerHTML = `
      <header class="topbar">
        <div class="top-left">${EMBLEM}<div class="top-title">MERIT SYSTEM<small>PERSONEL DIGITAL SYSTEM</small></div></div>
        <div class="user-menu">
          <button class="avatar-btn" id="user-btn" type="button"><div class="avatar">${esc(initials(ME.username))}</div>
            <div class="who"><b>${esc(ME.username)}</b><small>${roleLabel(ME.role)}</small></div></button>
          <div class="dropdown hidden" id="user-dd">
            <div class="dd-head"><div class="avatar">${esc(initials(ME.username))}</div><div><b>${esc(ME.username)}</b><br><small style="color:var(--muted)">${esc(ME.email)}</small></div></div>
            <div>Role</div><div style="margin-top:6px">${roleBadge(ME.role)}</div>
            <button class="dd-item" id="logout-btn" type="button">⎋ Keluar</button>
          </div>
        </div>
      </header>
      <div class="shell">
        <aside class="sidebar"><div class="nav-label">Menu</div><nav class="nav">${items}</nav>
          <div class="nav-label">Dokumentasi</div><nav class="nav"><a href="/docs" target="_blank"><span class="ic">📘</span>Swagger API</a></nav></aside>
        <main class="content" id="view">${inner}</main>
      </div>`;
    document.getElementById('user-btn').addEventListener('click', (e) => { e.stopPropagation(); document.getElementById('user-dd').classList.toggle('hidden'); });
    document.addEventListener('click', () => { const d = document.getElementById('user-dd'); if (d) d.classList.add('hidden'); });
    document.getElementById('logout-btn').addEventListener('click', () => logout());
  }
  const setView = (html) => { document.getElementById('view').innerHTML = html; };

  /* ===================== LOGIN ===================== */
  function renderLogin() {
    $app.innerHTML = `<div class="login-wrap"><div class="login-card">
      <div class="login-brand">${EMBLEM}<div class="brand-title">MERIT SYSTEM</div><div class="brand-sub">Personel Digital System</div></div>
      <h1>Selamat Datang</h1>
      <p class="lead">Silakan masukkan NRP/Username dan kata sandi Anda untuk menggunakan layanan ini.</p>
      <div id="login-err"></div>
      <form id="login-form" novalidate>
        <div class="field"><label>NRP / Username</label><input class="input" name="username" autocomplete="username" placeholder="NRP / Username" autofocus></div>
        <div class="field"><label>Password</label><div class="pw-wrap"><input class="input" type="password" name="password" autocomplete="current-password" placeholder="Password"><button type="button" id="pw-toggle">Lihat</button></div></div>
        <div class="row-between"><label class="check"><input type="checkbox" name="remember"> Ingat Saya</label><a href="#" id="forgot">Lupa Password</a></div>
        <button class="btn btn-primary btn-block" id="login-btn" type="submit">Masuk</button>
      </form>
      <div class="demo-box"><b>Akun demo</b> (klik untuk mengisi otomatis)
        <div class="demo-chips">
          <span class="chip" data-u="admin.ssdm" data-p="Admin@12345">Admin SSDM</span>
          <span class="chip" data-u="operator.metro" data-p="Operator@123">Operator Metro</span>
          <span class="chip" data-u="operator.jabar" data-p="Operator@123">Operator Jabar</span>
          <span class="chip" data-u="operator.jatim" data-p="Operator@123">Operator Jatim</span>
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

  /* ===================== DASHBOARD ===================== */
  async function pageDashboard() {
    layout('#/', '<div class="loading"><span class="spinner" style="border-color:#ccd;border-top-color:var(--blue)"></span> Memuat dashboard...</div>');
    const s = await api('GET', '/dashboard/stats');
    const maxP = Math.max(1, ...s.per_pangkat.map((x) => x.total));
    const maxS = Math.max(1, ...s.per_satker.map((x) => x.total));
    const bars = (rows, max, key) => rows.length ? rows.map((r) =>
      `<div class="bar-row"><div class="name" title="${esc(r[key])}">${esc(r[key])}</div><div class="bar"><i style="width:${(r.total / max) * 100}%"></i></div><div class="n">${r.total}</div></div>`).join('')
      : '<div class="empty">Belum ada data</div>';
    const adminStats = isAdmin()
      ? `<div class="stat orange"><div class="lbl">Satuan Kerja</div><div class="val">${s.total_satker}</div></div>
         <div class="stat red"><div class="lbl">Pengguna Sistem</div><div class="val">${s.total_user}</div></div>` : '';
    const modules = `
      <a class="module" href="#/personel"><span class="mi">👮</span>Data Personel</a>
      <a class="module" href="#/satker"><span class="mi">🏢</span>Satuan Kerja</a>
      ${isAdmin() ? '<a class="module" href="#/users"><span class="mi">👥</span>User Management</a>' : ''}
      <a class="module" href="/docs" target="_blank"><span class="mi">📘</span>API Documentation</a>`;
    const recent = s.personel_terbaru.length ? s.personel_terbaru.map((p) =>
      `<tr><td><a href="#/personel/${p.id}"><b>${esc(p.nama)}</b></a></td><td>${esc(p.nrp_nip)}</td><td>${esc(p.pangkat)}</td><td>${esc(p.satker_nama)}</td></tr>`).join('')
      : '<tr><td colspan="4" class="empty">Belum ada personel</td></tr>';
    setView(`
      <div class="hero"><h2>Selamat datang, ${esc(ME.username)}</h2>
        <p>Pengelolaan kualifikasi dan riwayat jabatan personel untuk mendukung penerapan sistem merit.</p>
        <span class="scope">${isAdmin() ? 'Cakupan: Seluruh Satuan Kerja' : 'Cakupan: Satker Anda'}</span></div>
      <div class="grid g4">
        <div class="stat green"><div class="lbl">Total Personel</div><div class="val">${s.total_personel}</div></div>
        <div class="stat"><div class="lbl">Total Riwayat Jabatan</div><div class="val">${s.total_riwayat_jabatan}</div></div>
        <div class="stat gold"><div class="lbl">Jabatan Aktif</div><div class="val">${s.jabatan_aktif}</div></div>
        ${adminStats}
      </div>
      <div class="modules">${modules}</div>
      <div class="grid g2">
        <div class="card"><h3>Personel per Pangkat</h3>${bars(s.per_pangkat, maxP, 'pangkat')}</div>
        <div class="card"><h3>Personel per Satuan Kerja</h3>${bars(s.per_satker, maxS, 'nama')}</div>
      </div>
      <div class="card" style="margin-top:16px"><h3>Personel Terbaru</h3>
        <div class="table-wrap"><table><thead><tr><th>Nama</th><th>NRP/NIP</th><th>Pangkat</th><th>Satker</th></tr></thead><tbody>${recent}</tbody></table></div></div>`);
  }

  /* ===================== PERSONEL LIST ===================== */
  let SATKERS = [];
  async function loadSatkers() { SATKERS = (await api('GET', '/satker?limit=100')).data; return SATKERS; }
  const satkerOptions = (sel, lockToOwn) => SATKERS
    .filter((s) => !lockToOwn || s.id === ME.satker_id)
    .map((s) => `<option value="${s.id}" ${s.id === sel ? 'selected' : ''}>${esc(s.nama)} (${esc(s.kode)})</option>`).join('');

  const listState = { skip: 0, limit: 10, nama: '', nrp_nip: '', pangkat: '', satker_id: '' };

  async function pagePersonel() {
    layout('#/personel', '<div class="loading">Memuat...</div>');
    await loadSatkers();
    setView(`
      <div class="page-head"><div><div class="crumb">Beranda › Personel</div><h2>Data Personel</h2></div>
        <button class="btn btn-gold" id="add-p">+ Tambah Personel</button></div>
      <div class="card">
        <div class="toolbar">
          <input class="input" id="f-nama" placeholder="Cari nama" value="${esc(listState.nama)}">
          <input class="input" id="f-nrp" placeholder="NRP / NIP" value="${esc(listState.nrp_nip)}">
          <input class="input" id="f-pangkat" placeholder="Pangkat" value="${esc(listState.pangkat)}">
          ${isAdmin() ? `<select class="select" id="f-satker"><option value="">Semua Satker</option>${satkerOptions(listState.satker_id)}</select>` : ''}
          <button class="btn btn-navy" id="f-go">Cari</button><button class="btn btn-ghost" id="f-reset">Reset</button>
        </div>
        <div id="plist"><div class="loading">Memuat data...</div></div>
      </div>`);
    document.getElementById('add-p').addEventListener('click', () => personelForm());
    const apply = () => {
      listState.nama = document.getElementById('f-nama').value.trim();
      listState.nrp_nip = document.getElementById('f-nrp').value.trim();
      listState.pangkat = document.getElementById('f-pangkat').value.trim();
      const fs = document.getElementById('f-satker'); listState.satker_id = fs ? fs.value : '';
      listState.skip = 0; refreshList();
    };
    document.getElementById('f-go').addEventListener('click', apply);
    ['f-nama', 'f-nrp', 'f-pangkat'].forEach((id) => document.getElementById(id).addEventListener('keydown', (e) => { if (e.key === 'Enter') apply(); }));
    document.getElementById('f-reset').addEventListener('click', () => { Object.assign(listState, { skip: 0, nama: '', nrp_nip: '', pangkat: '', satker_id: '' }); pagePersonel(); });
    refreshList();
  }

  async function refreshList() {
    const box = document.getElementById('plist');
    if (!box) return;
    box.innerHTML = '<div class="loading">Memuat data...</div>';
    const q = new URLSearchParams({ skip: listState.skip, limit: listState.limit });
    ['nama', 'nrp_nip', 'pangkat', 'satker_id'].forEach((k) => { if (listState[k]) q.set(k, listState[k]); });
    try {
      const r = await api('GET', '/personel?' + q.toString());
      const rows = r.data.length ? r.data.map((p, i) => `
        <tr><td>${listState.skip + i + 1}</td><td><a href="#/personel/${p.id}"><b>${esc(p.nama)}</b></a></td><td>${esc(p.nrp_nip)}</td>
        <td>${esc(p.pangkat)}</td><td>${esc(p.satker_nama)}</td><td>${esc(p.tempat_lahir)}, ${fmtDate(p.tanggal_lahir)}</td>
        <td><div class="actions"><a class="btn btn-ghost btn-sm" href="#/personel/${p.id}">Detail</a>
        <button class="btn btn-ghost btn-sm" data-edit="${p.id}">Edit</button>
        <button class="btn btn-danger btn-sm" data-del="${p.id}" data-name="${esc(p.nama)}">Hapus</button></div></td></tr>`).join('')
        : '<tr><td colspan="7" class="empty">Data tidak ditemukan</td></tr>';
      const page = Math.floor(r.skip / r.limit) + 1;
      box.innerHTML = `<div class="table-wrap"><table><thead><tr><th>No</th><th>Nama</th><th>NRP/NIP</th><th>Pangkat</th><th>Satker</th><th>Tempat, Tgl Lahir</th><th>Aksi</th></tr></thead><tbody>${rows}</tbody></table></div>
        <div class="pager"><div>Total ${r.total} personel • Halaman ${page} dari ${Math.max(r.pages, 1)}</div>
        <div class="btns"><button class="btn btn-ghost btn-sm" id="pg-prev" ${r.skip <= 0 ? 'disabled' : ''}>‹ Sebelumnya</button>
        <button class="btn btn-ghost btn-sm" id="pg-next" ${r.skip + r.limit >= r.total ? 'disabled' : ''}>Berikutnya ›</button></div></div>`;
      document.getElementById('pg-prev').addEventListener('click', () => { listState.skip = Math.max(0, listState.skip - listState.limit); refreshList(); });
      document.getElementById('pg-next').addEventListener('click', () => { listState.skip += listState.limit; refreshList(); });
      box.querySelectorAll('[data-edit]').forEach((b) => b.addEventListener('click', async () => {
        const d = await api('GET', '/personel/' + b.dataset.edit); personelForm(d);
      }));
      box.querySelectorAll('[data-del]').forEach((b) => b.addEventListener('click', () =>
        confirmBox('Hapus Personel', `Hapus <b>${esc(b.dataset.name)}</b> beserta seluruh riwayat jabatannya? Tindakan ini tidak dapat dibatalkan.`,
          async () => { await api('DELETE', '/personel/' + b.dataset.del); toast('Personel dihapus', 'ok'); refreshList(); })));
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
        <div class="field"><label>Pangkat *</label><input class="input" name="pangkat" value="${esc(p?.pangkat)}" placeholder="mis. IPDA, AKP, KOMPOL"></div>
        <div class="field"><label>Tempat Lahir *</label><input class="input" name="tempat_lahir" value="${esc(p?.tempat_lahir)}"></div>
        <div class="field"><label>Tanggal Lahir *</label><input class="input" type="date" name="tanggal_lahir" value="${esc(p?.tanggal_lahir)}"></div>
        <div class="field full"><label>Satuan Kerja *</label><select class="select" name="satker_id" ${lock ? 'data-lock' : ''}>${satkerOptions(p?.satker_id || (lock ? ME.satker_id : ''), lock)}</select></div></div>`,
      onSubmit: async (f, close) => {
        const body = { nama: f.nama, pangkat: f.pangkat, tempat_lahir: f.tempat_lahir, tanggal_lahir: f.tanggal_lahir, satker_id: f.satker_id };
        if (!edit) { body.nrp_nip = f.nrp_nip; await api('POST', '/personel', body); toast('Personel ditambahkan', 'ok'); }
        else { await api('PUT', '/personel/' + p.id, body); toast('Personel diperbarui', 'ok'); }
        close();
        if (location.hash.startsWith('#/personel/')) route(); else refreshList();
      },
    });
  }

  /* ===================== PERSONEL DETAIL ===================== */
  async function pageDetail(id) {
    layout('#/personel', '<div class="loading">Memuat profil...</div>');
    await loadSatkers();
    let p;
    try { p = await api('GET', '/personel/' + id); } catch (err) {
      setView(`<div class="err">${esc(err.message)}</div><a class="btn btn-ghost" href="#/personel">‹ Kembali</a>`); return;
    }
    const aktif = p.jabatan_aktif;
    const rows = p.riwayat_jabatan.length ? p.riwayat_jabatan.map((r, i) => `
      <tr><td>${i + 1}</td><td><b>${esc(r.jabatan)}</b></td><td>${esc(r.satuan_kerja)}</td><td>${esc(r.fungsi)}</td><td>${esc(r.nivelering_jabatan)}</td>
      <td>${fmtDate(r.tanggal_mulai)}</td><td>${r.tanggal_berakhir ? fmtDate(r.tanggal_berakhir) : '<i>sekarang</i>'}</td>
      <td><span class="badge ${r.status_jabatan === 'AKTIF' ? 'badge-ok' : 'badge-off'}">${r.status_jabatan === 'AKTIF' ? 'Aktif' : 'Non Aktif'}</span></td>
      <td>${esc(r.keterangan || '-')}</td>
      <td><div class="actions"><button class="btn btn-ghost btn-sm" data-redit="${r.id}">Edit</button><button class="btn btn-danger btn-sm" data-rdel="${r.id}">Hapus</button></div></td></tr>`).join('')
      : '<tr><td colspan="10" class="empty">Belum ada riwayat jabatan</td></tr>';
    const timeline = p.riwayat_jabatan.length ? p.riwayat_jabatan.map((r) => `
      <div class="tl-item ${r.status_jabatan === 'AKTIF' ? 'aktif' : ''}"><h4>${esc(r.jabatan)} ${r.status_jabatan === 'AKTIF' ? '<span class="badge badge-ok">Saat ini</span>' : ''}</h4>
      <div class="meta">${esc(r.satuan_kerja)} • ${esc(r.fungsi)} • ${esc(r.nivelering_jabatan)}</div>
      <div class="meta">${fmtDate(r.tanggal_mulai)} — ${r.tanggal_berakhir ? fmtDate(r.tanggal_berakhir) : 'sekarang'}</div></div>`).join('')
      : '<div class="empty">Belum ada riwayat jabatan</div>';

    setView(`
      <div class="page-head"><div><div class="crumb"><a href="#/personel">Personel</a> › Profil</div><h2>Profil Personel</h2></div>
        <div class="actions"><a class="btn btn-ghost" href="#/personel">‹ Kembali</a><button class="btn btn-ghost" id="ed-p">Edit Data</button><button class="btn btn-danger" id="del-p">Hapus</button></div></div>
      <div class="card"><div class="profile"><div class="pbig">${esc(initials(p.nama))}</div>
        <div><h2 style="font-size:20px">${esc(p.nama)}</h2><div style="color:var(--muted)">${esc(p.pangkat)} • NRP/NIP ${esc(p.nrp_nip)}</div></div></div>
        <div class="kv"><div><small>Tempat, Tanggal Lahir</small><b>${esc(p.tempat_lahir)}, ${fmtDate(p.tanggal_lahir)}</b></div>
        <div><small>Satuan Kerja</small><b>${esc(p.satker_nama)}</b></div>
        <div><small>Jabatan Saat Ini</small><b>${aktif ? esc(aktif.jabatan) : '-'}</b></div>
        <div><small>Total Riwayat Jabatan</small><b>${p.total_riwayat_jabatan}</b></div></div></div>
      <div class="tabs"><button class="tab active" data-tab="t1">Perjalanan Karier</button><button class="tab" data-tab="t2">Riwayat Jabatan (Tabel)</button></div>
      <div id="t1" class="card"><div class="timeline">${timeline}</div></div>
      <div id="t2" class="card hidden"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px"><h3 style="margin:0">Riwayat Jabatan</h3><button class="btn btn-gold btn-sm" id="add-rj">+ Tambah</button></div>
        <div class="table-wrap"><table><thead><tr><th>No</th><th>Jabatan</th><th>Satuan Kerja</th><th>Fungsi</th><th>Nivelering</th><th>TMT</th><th>Berakhir</th><th>Status</th><th>Keterangan</th><th>Aksi</th></tr></thead><tbody>${rows}</tbody></table></div></div>`);
    document.querySelectorAll('.tab').forEach((t) => t.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach((x) => x.classList.toggle('active', x === t));
      ['t1', 't2'].forEach((k) => document.getElementById(k).classList.toggle('hidden', k !== t.dataset.tab));
    }));
    document.getElementById('ed-p').addEventListener('click', () => personelForm(p));
    document.getElementById('del-p').addEventListener('click', () => confirmBox('Hapus Personel', `Hapus <b>${esc(p.nama)}</b> beserta seluruh riwayat jabatannya?`,
      async () => { await api('DELETE', '/personel/' + p.id); toast('Personel dihapus', 'ok'); location.hash = '#/personel'; }));
    document.getElementById('add-rj').addEventListener('click', () => jabatanForm(p.id));
    document.querySelectorAll('[data-redit]').forEach((b) => b.addEventListener('click', () => jabatanForm(p.id, p.riwayat_jabatan.find((x) => x.id === b.dataset.redit))));
    document.querySelectorAll('[data-rdel]').forEach((b) => b.addEventListener('click', () => confirmBox('Hapus Riwayat Jabatan', 'Hapus riwayat jabatan ini?',
      async () => { await api('DELETE', `/personel/${p.id}/riwayat-jabatan/${b.dataset.rdel}`); toast('Riwayat jabatan dihapus', 'ok'); pageDetail(p.id).then(() => document.querySelector('[data-tab=t2]').click()); })));
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
        close();
        pageDetail(pid).then(() => document.querySelector('[data-tab=t2]').click());
      },
    });
  }

  /* ===================== SATKER ===================== */
  async function pageSatker() {
    layout('#/satker', '<div class="loading">Memuat...</div>');
    await loadSatkers();
    const rows = SATKERS.length ? SATKERS.map((s, i) => `<tr><td>${i + 1}</td><td><b>${esc(s.nama)}</b></td><td>${esc(s.kode)}</td><td>${esc(s.deskripsi || '-')}</td>
      ${isAdmin() ? `<td><div class="actions"><button class="btn btn-ghost btn-sm" data-sedit="${s.id}">Edit</button><button class="btn btn-danger btn-sm" data-sdel="${s.id}" data-name="${esc(s.nama)}">Hapus</button></div></td>` : ''}</tr>`).join('')
      : '<tr><td colspan="5" class="empty">Belum ada satker</td></tr>';
    setView(`<div class="page-head"><div><div class="crumb">Beranda › Satuan Kerja</div><h2>Satuan Kerja</h2></div>
      ${isAdmin() ? '<button class="btn btn-gold" id="add-s">+ Tambah Satker</button>' : ''}</div>
      <div class="card"><div class="table-wrap"><table><thead><tr><th>No</th><th>Nama</th><th>Kode</th><th>Deskripsi</th>${isAdmin() ? '<th>Aksi</th>' : ''}</tr></thead><tbody>${rows}</tbody></table></div></div>`);
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

  /* ===================== USERS (ADMIN) ===================== */
  async function pageUsers() {
    layout('#/users', '<div class="loading">Memuat...</div>');
    await loadSatkers();
    const users = await api('GET', '/users?limit=100');
    const sname = (id) => (SATKERS.find((s) => s.id === id) || {}).nama || '-';
    const rows = users.map((u, i) => `<tr><td>${i + 1}</td><td><b>${esc(u.username)}</b></td><td>${esc(u.email)}</td><td>${roleBadge(u.role)}</td><td>${esc(sname(u.satker_id))}</td>
      <td><span class="badge ${u.is_active ? 'badge-ok' : 'badge-off'}">${u.is_active ? 'Aktif' : 'Nonaktif'}</span></td>
      <td><div class="actions"><button class="btn btn-ghost btn-sm" data-uedit="${u.id}">Edit</button>
      <button class="btn btn-danger btn-sm" data-udel="${u.id}" data-name="${esc(u.username)}" ${u.id === ME.id ? 'disabled' : ''}>Hapus</button></div></td></tr>`).join('');
    setView(`<div class="page-head"><div><div class="crumb">Beranda › Manajemen User</div><h2>Manajemen User</h2></div><button class="btn btn-gold" id="add-u">+ Tambah User</button></div>
      <div class="card"><div class="table-wrap"><table><thead><tr><th>No</th><th>Username</th><th>Email</th><th>Role</th><th>Satker</th><th>Status</th><th>Aksi</th></tr></thead><tbody>${rows}</tbody></table></div></div>`);
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
      if (h === '#/' || h === '#' || h === '#/login') { if (h === '#/login') location.hash = '#/'; return await pageDashboard(); }
      if (h === '#/personel') return await pagePersonel();
      if (h.startsWith('#/personel/')) return await pageDetail(h.split('/')[2]);
      if (h === '#/satker') return await pageSatker();
      if (h === '#/users') { if (!isAdmin()) { toast('Halaman khusus Admin SSDM', 'bad'); location.hash = '#/'; return; } return await pageUsers(); }
      location.hash = '#/';
    } catch (err) {
      if (ME) { layout(h, `<div class="err">${esc(err.message)}</div>`); }
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
