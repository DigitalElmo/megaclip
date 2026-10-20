// MegaClip search: filters the home page grid, adds PC-port matches (loaded only when someone searches),
// sends searches from other pages to the home page, and runs the PC Ports page search.
(() => {
  const $ = id => document.getElementById(id);
  let D = null;
  const load = () => D ? Promise.resolve(D) : fetch('/search-decomps.json').then(r => r.json()).then(j => (D = j));
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const words = v => v.toLowerCase().split(/\s+/).filter(Boolean);
  // row = [slug, title, platform, family, status, url]; slug is empty when the game has no page of its own
  const hit = (r, w) => { const h = (r[1] + ' ' + r[2] + ' ' + r[3]).toLowerCase(); return w.every(x => h.includes(x)); };
  const link = r => r[0] ? `<a href="/decomp/${r[0]}">${esc(r[1])}</a>`
    : `<a href="${esc(r[5])}" target="_blank" rel="noopener noreferrer">${esc(r[1])}</a>`;
  const S = { easy: 'Easy install', play: 'PC version', code: 'Code only', wip: 'In progress' };
  const params = new URLSearchParams(location.search);
  const q = $('q'), go = $('go'), home = $('home');

  if (q && home) {
    const cards = [...home.querySelectorAll('.c')], boxes = [...home.querySelectorAll('.box:not(#dbox)')];
    const nr = $('nores'), ph = $('ph'), db = $('dbox'), dl = $('dl');
    const f = () => {
      const v = q.value.trim().toLowerCase(), po = ph && ph.checked;
      let any = 0;
      cards.forEach(c => c.classList.toggle('hide', (!!v && !c.dataset.s.includes(v)) || (po && c.dataset.m !== 'yes')));
      boxes.forEach(b => { const n = b.querySelectorAll('.c:not(.hide)').length; b.classList.toggle('hide', !n); any += n; });
      nr.classList.toggle('hide', !!any || !(v || po));
      if (v.length < 3) { db.hidden = true; return; }
      load().then(D => {
        if (q.value.trim().toLowerCase() !== v) return;
        const m = D.filter(r => hit(r, words(v))).sort((a, b) => (!a[0]) - (!b[0]));
        db.hidden = !m.length;
        $('dn').textContent = m.length + ' found';
        dl.innerHTML = m.slice(0, 24).map(r => `<li>${link(r)} <small>${esc(r[2])}</small></li>`).join('') +
          (m.length > 24 ? `<li><a href="/decomps?q=${encodeURIComponent(v)}"><b>See all ${m.length} &raquo;</b></a></li>` : '');
      }).catch(() => { db.hidden = true; });
    };
    if (ph) ph.addEventListener('change', f);
    q.addEventListener('input', f);
    if (go) go.onclick = f;
    if (params.get('q')) { q.value = params.get('q'); f(); }
  } else if (q) {
    const send = () => { const v = q.value.trim(); if (v) location.href = '/?q=' + encodeURIComponent(v); };
    q.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });
    if (go) go.onclick = send;
  }

  const dq = $('dq');
  if (dq) {
    const df = $('df'), ds = $('ds'), res = $('dres'), all = $('dall'), cnt = $('dcount');
    const g = () => {
      const v = dq.value.trim(), fam = df.value, st = ds.value;
      if (!v && !fam && st === 'pc') { res.hidden = true; all.hidden = false; cnt.textContent = ''; return; }
      load().then(D => {
        const w = words(v);
        const m = D.filter(r => hit(r, w) && (!fam || r[3] === fam) &&
          (st === '' || (st === 'pc' ? (r[4] === 'easy' || r[4] === 'play') : r[4] === st)));
        all.hidden = true; res.hidden = false;
        cnt.textContent = m.length.toLocaleString() + ' games';
        res.innerHTML = m.slice(0, 300).map(r => `<li>${link(r)} <small>${esc(r[2])} &middot; ${S[r[4]]}${r[0] ? '' : ' &middot; opens the project page'}</small></li>`).join('') +
          (m.length > 300 ? '<li>Showing the first 300. Type more to narrow it down.</li>' : '') +
          (m.length ? '' : '<li>No games match. Try another word or pick "Everything".</li>');
      }).catch(() => { cnt.textContent = 'Search could not load. Refresh the page to try again.'; });
    };
    dq.addEventListener('input', g); df.addEventListener('change', g); ds.addEventListener('change', g);
    if (params.get('q')) { dq.value = params.get('q'); g(); }
  }
})();
