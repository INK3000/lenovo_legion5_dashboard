HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Local Dashboard</title>
  <style>
    /* Local fonts — served from /static/fonts/ if available */
    @font-face {
      font-family: 'IBM Plex Mono';
      font-style: normal; font-weight: 400;
      src: url('/static/fonts/IBMPlexMono-Regular.woff2') format('woff2');
      font-display: swap;
    }
    @font-face {
      font-family: 'IBM Plex Mono';
      font-style: normal; font-weight: 500;
      src: url('/static/fonts/IBMPlexMono-Medium.woff2') format('woff2');
      font-display: swap;
    }
    @font-face {
      font-family: 'IBM Plex Mono';
      font-style: normal; font-weight: 600;
      src: url('/static/fonts/IBMPlexMono-SemiBold.woff2') format('woff2');
      font-display: swap;
    }
    @font-face {
      font-family: 'IBM Plex Sans';
      font-style: normal; font-weight: 400;
      src: url('/static/fonts/IBMPlexSans-Regular.woff2') format('woff2');
      font-display: swap;
    }
    @font-face {
      font-family: 'IBM Plex Sans';
      font-style: normal; font-weight: 500;
      src: url('/static/fonts/IBMPlexSans-Medium.woff2') format('woff2');
      font-display: swap;
    }
    @font-face {
      font-family: 'IBM Plex Sans';
      font-style: normal; font-weight: 600;
      src: url('/static/fonts/IBMPlexSans-SemiBold.woff2') format('woff2');
      font-display: swap;
    }
  </style>
  <script>
    // Use local Tailwind if available, fallback to CDN
    (function() {
      var s = document.createElement('script');
      s.src = '/static/tailwind.js';
      s.onerror = function() {
        var f = document.createElement('script');
        f.src = 'https://cdn.tailwindcss.com';
        document.head.appendChild(f);
      };
      document.head.appendChild(s);
    })();
  </script>
  <script>
    // Tailwind config — must run after tailwind loads, use MutationObserver trick
    function applyTailwindConfig() {
      if (typeof tailwind === 'undefined') { setTimeout(applyTailwindConfig, 50); return; }
      tailwind.config = {
      theme: {
        extend: {
          fontFamily: {
            mono: ['IBM Plex Mono', 'monospace'],
            sans: ['IBM Plex Sans', 'sans-serif'],
          },
          colors: {
            surface: '#0f0f0f',
            panel:   '#161616',
            border:  '#2a2a2a',
            muted:   '#555',
            label:   '#888',
            text:    '#e8e8e8',
            accent:  '#c8f03c',
          }
        }
      }
    };
    }
    applyTailwindConfig();
  </script>
  <style>
    * { box-sizing: border-box; }
    body { background: #0f0f0f; color: #e8e8e8; font-family: 'IBM Plex Sans', sans-serif; }
    .font-mono { font-family: 'IBM Plex Mono', monospace; }

    /* Scanline overlay for industrial feel */
    body::before {
      content: '';
      position: fixed; inset: 0; pointer-events: none; z-index: 9999;
      background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,0,0,0.04) 2px,
        rgba(0,0,0,0.04) 4px
      );
    }

    canvas { display: block; }

    .kpi-val {
      font-family: 'IBM Plex Mono', monospace;
      font-size: 1.1rem;
      font-weight: 600;
      line-height: 1.2;
      letter-spacing: -0.02em;
    }

    .status-badge {
      display: inline-flex; align-items: center; gap: 6px;
      padding: 3px 10px 3px 8px;
      border-radius: 999px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 0.75rem;
      font-weight: 500;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }
    .badge-charging   { background: rgba(200,240,60,0.12);  color: #c8f03c; border: 1px solid rgba(200,240,60,0.3); }
    .badge-discharging{ background: rgba(255,160,60,0.12);  color: #ffa03c; border: 1px solid rgba(255,160,60,0.3); }
    .badge-full       { background: rgba(60,200,120,0.12);  color: #3cc878; border: 1px solid rgba(60,200,120,0.3); }
    .badge-unknown    { background: rgba(100,100,100,0.12); color: #888;    border: 1px solid rgba(100,100,100,0.3); }

    .dot {
      width: 7px; height: 7px; border-radius: 50%;
    }
    .dot-charging    { background: #c8f03c; box-shadow: 0 0 6px #c8f03c; animation: pulse 1.5s infinite; }
    .dot-discharging { background: #ffa03c; }
    .dot-full        { background: #3cc878; }
    .dot-unknown     { background: #888; }

    @keyframes pulse {
      0%,100% { opacity:1; } 50% { opacity:0.3; }
    }

    .toggle-track {
      width: 42px; height: 24px;
      border-radius: 12px;
      background: #2a2a2a;
      border: 1px solid #3a3a3a;
      cursor: pointer;
      transition: background 0.2s;
      position: relative;
      flex-shrink: 0;
    }
    .toggle-track.on {
      background: rgba(200,240,60,0.2);
      border-color: rgba(200,240,60,0.5);
    }
    .toggle-thumb {
      position: absolute;
      top: 3px; left: 3px;
      width: 16px; height: 16px;
      border-radius: 50%;
      background: #555;
      transition: transform 0.2s, background 0.2s;
    }
    .toggle-track.on .toggle-thumb {
      transform: translateX(18px);
      background: #c8f03c;
    }
    .toggle-track.loading { opacity: 0.5; pointer-events: none; }
  </style>
</head>
<body class="min-h-screen p-4">

  <!-- Header -->
  <div class="flex items-center justify-between mb-3 border-b border-border pb-3">
    <div class="flex items-center gap-3">
      <div class="font-mono text-accent font-semibold tracking-widest text-sm uppercase">Local Dashboard</div>
      <div class="w-px h-4 bg-border"></div>
      <div class="font-mono text-muted text-xs" id="headerBat">BAT0</div>
    </div>
    <div class="font-mono text-muted text-xs" id="lastUpdate">—</div>
  </div>

  <!-- Tabs -->
  <div class="flex gap-2 mb-3">
    <button onclick="switchTab('battery')" id="tab-battery"
      class="tab-btn font-mono text-xs uppercase tracking-widest px-3 py-1.5 rounded-lg border border-accent text-accent">
      Battery
    </button>
    <button onclick="switchTab('procs')" id="tab-procs"
      class="tab-btn font-mono text-xs uppercase tracking-widest px-3 py-1.5 rounded-lg border border-border text-muted">
      Processes
    </button>
  </div>

  <!-- Panel: Battery -->
  <div id="panel-battery">

  <!-- KPI row —  cards -->
  <div class="grid grid-cols-3 gap-2 mb-2 sm:grid-cols-5">

    <div class="bg-panel border border-border rounded-lg px-3 py-2.5 flex flex-col gap-1">
      <div class="text-label text-xs font-mono uppercase tracking-widest leading-none">Charge</div>
      <div class="flex items-end gap-2">
        <div class="kpi-val text-text" id="kpiPct">—</div>
      </div>
      <div class="h-0.5 rounded-full bg-border overflow-hidden mt-0.5">
        <div id="pctBar" class="h-full rounded-full bg-accent transition-all duration-700" style="width:0%"></div>
      </div>
    </div>

    <div class="bg-panel border border-border rounded-lg px-3 py-2.5 flex flex-col gap-1">
      <div class="text-label text-xs font-mono uppercase tracking-widest leading-none">Status</div>
      <div id="kpiStatus"><span class="kpi-val text-muted">—</span></div>
    </div>

    <div class="bg-panel border border-border rounded-lg px-3 py-2.5 flex flex-col gap-1">
      <div class="text-label text-xs font-mono uppercase tracking-widest leading-none">Uptime</div>
      <div class="kpi-val text-text" id="sysUptime">—</div>
    </div>

    <div class="bg-panel border border-border rounded-lg px-3 py-2.5 flex flex-col gap-1">
      <div class="text-label text-xs font-mono uppercase tracking-widest leading-none">Power</div>
      <div class="kpi-val text-text" id="kpiW">—</div>
    </div>

    <div class="bg-panel border border-border rounded-lg px-3 py-2.5 flex flex-col gap-1">
      <div class="text-label text-xs font-mono uppercase tracking-widest leading-none">ETA</div>
      <div class="flex items-baseline gap-1.5">
        <div class="kpi-val text-text" id="kpiEta">—</div>
        <div class="text-muted text-xs font-mono" id="kpiEtaLabel"></div>
      </div>
    </div>

  </div>

  <!-- Conservation mode card — compact inline -->
  <div class="bg-panel border border-border rounded-lg px-3 py-2 mb-2 flex items-center justify-between" id="conservCard">
    <div class="flex items-center gap-3">
      <div class="text-label text-xs font-mono uppercase tracking-widest">Conservation Mode</div>
      <div class="text-text text-xs font-mono text-muted">limit charge to ~80%</div>
    </div>
    <div class="flex items-center gap-3">
      <span class="font-mono text-xs text-muted" id="conservLabel">—</span>
      <div class="toggle-track" id="conservToggle" onclick="toggleConservation()">
        <div class="toggle-thumb"></div>
      </div>
    </div>
  </div>

  <!-- Chart — fills remaining vertical space -->
  <div class="bg-panel border border-border rounded-xl p-3">
    <div class="flex items-center justify-between mb-2">
      <div class="text-label text-xs font-mono uppercase tracking-widest">Charge History</div>
      <div class="font-mono text-xs text-muted" id="kpiWindow">—</div>
    </div>
    <canvas id="chart" style="width:100%"></canvas>
    <div class="flex items-center gap-4 mt-2 text-muted text-xs font-mono">
      <span>auto-refresh 10s</span>
      <span class="text-border">|</span>
      <span>endpoint: <span class="text-label">/api/battery</span></span>
    </div>
  </div>

  </div><!-- /panel-battery -->

  <!-- Panel: Processes -->
  <div id="panel-procs" style="display:none">
    <div class="bg-panel border border-border rounded-xl p-4">
      <div class="flex items-center justify-between mb-4">
        <div>
          <div class="text-text text-sm font-mono font-semibold">Top 10 · Current Power Usage</div>
          <div class="text-muted text-xs font-mono mt-0.5">Estimated from CPU time × total power draw</div>
        </div>
        <div class="font-mono text-xs text-muted" id="procsUpdated">—</div>
      </div>
      <div id="procsList">
        <div class="text-muted text-xs font-mono py-4">Collecting data… first sample takes ~15s</div>
      </div>
    </div>
  </div><!-- /panel-procs -->

<script>
// ── Tabs ──────────────────────────────────────────────────────────────────────
function switchTab(name) {
  ['battery', 'procs'].forEach(t => {
    const panel = document.getElementById('panel-' + t);
    const btn   = document.getElementById('tab-' + t);
    const active = t === name;
    panel.style.display = active ? 'block' : 'none';
    btn.classList.toggle('border-accent', active);
    btn.classList.toggle('text-accent',   active);
    btn.classList.toggle('border-border', !active);
    btn.classList.toggle('text-muted',    !active);
  });
  if (name === 'procs') loadProcs();
}

// ── Conservation mode ────────────────────────────────────────────────────────
let conservEnabled = null;

async function loadUptime() {
  try {
    const r = await fetch('/api/uptime', {cache:'no-store'});
    const j = await r.json();
    const s = j.seconds;
    const d = Math.floor(s / 86400);
    const h = Math.floor((s % 86400) / 3600);
    const m = Math.floor((s % 3600) / 60);
    let str = '';
    if (d > 0) str += `${d}d `;
    if (d > 0 || h > 0) str += `${h}h `;
    str += `${m}m`;
    document.getElementById('sysUptime').textContent = str;
  } catch(e) {}
}

async function loadConservation() {
  try {
    const r = await fetch('/api/conservation', {cache:'no-store'});
    const j = await r.json();
    if (j.available === false) {
      document.getElementById('conservCard').style.display = 'none';
      return;
    }
    conservEnabled = j.enabled;
    updateConservUI(j.enabled);
  } catch(e) {
    document.getElementById('conservCard').style.display = 'none';
  }
}

function updateConservUI(enabled) {
  const track = document.getElementById('conservToggle');
  const label = document.getElementById('conservLabel');
  track.classList.toggle('on', enabled);
  label.textContent = enabled ? 'ON' : 'OFF';
  label.style.color = enabled ? '#c8f03c' : '#555';
}

async function toggleConservation() {
  const track = document.getElementById('conservToggle');
  track.classList.add('loading');
  const newVal = !conservEnabled;
  try {
    const r = await fetch('/api/conservation', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({enabled: newVal})
    });
    const j = await r.json();
    conservEnabled = j.enabled;
    updateConservUI(j.enabled);
  } catch(e) {}
  track.classList.remove('loading');
}

// ── Battery status helpers ────────────────────────────────────────────────────
function statusClass(s) {
  const l = s.toLowerCase();
  if (l.includes('charg') && !l.includes('dis')) return 'charging';
  if (l.includes('discharg')) return 'discharging';
  if (l.includes('full')) return 'full';
  return 'unknown';
}

function statusBadge(s) {
  const cls = statusClass(s);
  return `<span class="status-badge badge-${cls}">
    <span class="dot dot-${cls}"></span>${s}
  </span>`;
}

function fmtEta(hours, status) {
  if (hours === null || hours === undefined) return {val: '—', label: ''};
  const s = status.toLowerCase();
  const totalMin = Math.round(hours * 60);
  let val;
  if (hours >= 1) {
    const h = Math.floor(hours);
    const m = Math.round((hours - h) * 60);
    val = m > 0 ? `${h}h ${m}m` : `${h}h`;
  } else {
    val = `${totalMin}m`;
  }
  let label = '';
  if (s.includes('discharg'))  label = 'until empty';
  else if (s.includes('charg')) label = 'until full';
  return {val, label};
}

// ── Canvas chart ──────────────────────────────────────────────────────────────
const canvas = document.getElementById('chart');
const ctx = canvas.getContext('2d');
let lastPoints = [];

function resizeCanvas() {
  const canvas = document.getElementById('chart');
  // How far from top of viewport is the canvas top edge?
  const top = canvas.getBoundingClientRect().top;
  // Footer row inside chart card (auto-refresh line) + card bottom padding + body bottom padding
  const bottomChrome = 40;
  const maxH = window.innerHeight * 0.9;
  const h = Math.max(120, Math.min(maxH, window.innerHeight * 0.9 - top - bottomChrome));
  canvas.style.height = h + 'px';

  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width  = Math.floor(rect.width  * dpr);
  canvas.height = Math.floor(rect.height * dpr);
  ctx.setTransform(dpr,0,0,dpr,0,0);
  drawLine(lastPoints);
}
window.addEventListener('resize', resizeCanvas);

function fmtAxisTime(minutes) {
  if (minutes >= 60) {
    const h = Math.floor(minutes / 60);
    const m = Math.round(minutes % 60);
    return m > 0 ? `${h}h${m}m` : `${h}h`;
  }
  return `${Math.round(minutes)}m`;
}

function drawLine(points) {
  lastPoints = points;
  const w = canvas.getBoundingClientRect().width;
  const h = canvas.getBoundingClientRect().height;
  ctx.clearRect(0,0,w,h);

  const padL=48, padR=16, padT=16, padB=36;
  const plotW = w - padL - padR;
  const plotH = h - padT - padB;

  // background grid
  ctx.font = '11px IBM Plex Mono, monospace';
  ctx.textAlign = 'right';

  for (let y = 0; y <= 100; y += 20) {
    const py = padT + (1 - y/100) * plotH;
    ctx.strokeStyle = y === 0 ? '#333' : '#222';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padL, py);
    ctx.lineTo(padL + plotW, py);
    ctx.stroke();
    ctx.fillStyle = '#555';
    ctx.fillText(String(y)+'%', padL - 6, py + 4);
  }

  // axes
  ctx.strokeStyle = '#333';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padL, padT);
  ctx.lineTo(padL, padT + plotH);
  ctx.lineTo(padL + plotW, padT + plotH);
  ctx.stroke();

  if (points.length < 2) {
    ctx.fillStyle = '#444';
    ctx.textAlign = 'left';
    ctx.fillText('Not enough data yet…', padL + 12, padT + 24);
    return;
  }

  const x0 = points[0].t;
  const xs = points.map(p => (p.t - x0) / 60.0);  // minutes
  const ys = points.map(p => p.pct);
  const xmax = Math.max(...xs) || 1;

  const xToPx = x => padL + (x / xmax) * plotW;
  const yToPx = y => padT + (1 - y/100) * plotH;

  // x-axis labels — adaptive, skip duplicates, show only if range is meaningful
  ctx.fillStyle = '#555';
  ctx.textAlign = 'center';
  if (xmax >= 1) {
    // pick a clean step: 1m, 2m, 5m, 10m, 15m, 30m, 1h, 2h, 3h, 6h...
    const steps = [1, 2, 5, 10, 15, 30, 60, 120, 180, 360, 720];
    const targetTicks = 5;
    const step = steps.find(s => xmax / s <= targetTicks) || steps[steps.length - 1];
    const seen = new Set();
    for (let v = 0; v <= xmax; v += step) {
      const label = fmtAxisTime(v);
      if (seen.has(label)) continue;
      seen.add(label);
      const px = padL + (v / xmax) * plotW;
      ctx.fillText(label, px, padT + plotH + 20);
    }
    // always show the rightmost label if it differs
    const lastLabel = fmtAxisTime(xmax);
    if (!seen.has(lastLabel)) {
      ctx.fillText(lastLabel, padL + plotW, padT + plotH + 20);
    }
  } else {
    // not enough data yet — just show a hint
    ctx.fillStyle = '#444';
    ctx.textAlign = 'left';
    ctx.fillText('accumulating data…', padL + 8, padT + plotH + 20);
  }

  // color per status
  function segColor(status) {
    const s = (status || '').toLowerCase();
    if (s.includes('charg') && !s.includes('dis')) return { line: '#3cf07c', fill: 'rgba(60,240,124,0.15)' };
    if (s.includes('discharg')) return { line: '#5b9cf6', fill: 'rgba(91,156,246,0.13)' };
    return { line: '#888', fill: 'rgba(136,136,136,0.08)' };
  }

  // split points into contiguous segments by status
  const segments = [];
  let seg = [0];
  for (let i = 1; i < points.length; i++) {
    const prevS = (points[i-1].status || '').toLowerCase();
    const curS  = (points[i].status  || '').toLowerCase();
    const sameGroup = (s) => {
      if (s.includes('charg') && !s.includes('dis')) return 'c';
      if (s.includes('discharg')) return 'd';
      return 'u';
    };
    if (sameGroup(prevS) !== sameGroup(curS)) {
      seg.push(i); segments.push(seg); seg = [i];
    } else {
      seg.push(i);
    }
  }
  segments.push(seg);

  // draw fill then line per segment
  segments.forEach(idxs => {
    if (idxs.length < 2) return;
    const col = segColor(points[idxs[0]].status);
    const sxs = idxs.map(i => xToPx(xs[i]));
    const sys = idxs.map(i => yToPx(ys[i]));
    const bot = padT + plotH;

    // fill
    const grad = ctx.createLinearGradient(0, padT, 0, bot);
    grad.addColorStop(0, col.fill.replace('0.15', '0.22').replace('0.13', '0.20').replace('0.08','0.12'));
    grad.addColorStop(1, col.fill.replace(/[\d.]+\)$/, '0)'));
    ctx.beginPath();
    ctx.moveTo(sxs[0], sys[0]);
    for (let i = 1; i < sxs.length; i++) ctx.lineTo(sxs[i], sys[i]);
    ctx.lineTo(sxs[sxs.length-1], bot);
    ctx.lineTo(sxs[0], bot);
    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.fill();

    // line
    ctx.strokeStyle = col.line;
    ctx.lineWidth = 2;
    ctx.lineJoin = 'round';
    ctx.beginPath();
    ctx.moveTo(sxs[0], sys[0]);
    for (let i = 1; i < sxs.length; i++) ctx.lineTo(sxs[i], sys[i]);
    ctx.stroke();
  });

  // last point — colored by current status
  const lastCol = segColor(points[points.length-1].status);
  const lx = xToPx(xs[xs.length-1]);
  const ly = yToPx(ys[ys.length-1]);
  ctx.fillStyle = lastCol.line;
  ctx.beginPath();
  ctx.arc(lx, ly, 4, 0, Math.PI*2);
  ctx.fill();
  // glow ring
  ctx.strokeStyle = lastCol.line.replace(')', ', 0.3)').replace('rgb', 'rgba') || lastCol.fill;
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.arc(lx, ly, 7, 0, Math.PI*2);
  ctx.stroke();
}

// ── Main refresh ──────────────────────────────────────────────────────────────
async function refresh() {
  try {
    const r = await fetch('/api/battery', {cache:'no-store'});
    const j = await r.json();

    document.getElementById('headerBat').textContent = j.battery;

    if (j.latest) {
      const pct = j.latest.pct;
      document.getElementById('kpiPct').textContent = `${pct}%`;
      document.getElementById('pctBar').style.width = `${pct}%`;

      document.getElementById('kpiStatus').innerHTML = statusBadge(j.latest.status || '—');

      document.getElementById('kpiW').textContent =
        j.latest.w !== null && j.latest.w !== undefined
          ? `${j.latest.w.toFixed(1)} W`
          : '—';

      const eta = fmtEta(j.latest.eta, j.latest.status || '');
      document.getElementById('kpiEta').textContent = eta.val;
      document.getElementById('kpiEtaLabel').textContent = eta.label;
    }

    document.getElementById('kpiWindow').textContent = `${j.points.length} samples`;
    document.getElementById('lastUpdate').textContent =
      'updated ' + new Date().toLocaleTimeString();

    drawLine(j.points);
  } catch(e) {
    console.error(e);
  }
}

// defer so browser has painted layout before we measure
requestAnimationFrame(() => { resizeCanvas(); refresh(); });
loadConservation();
loadUptime();
loadProcs();
setInterval(refresh, 10000);
setInterval(loadConservation, 15000);
setInterval(loadUptime, 60000);
setInterval(loadProcs, 15000);

// ── Process list ──────────────────────────────────────────────────────────────
async function loadProcs() {
  try {
    const r = await fetch('/api/procs', {cache:'no-store'});
    const j = await r.json();
    const list = j.procs || [];
    const el = document.getElementById('procsList');
    document.getElementById('procsUpdated').textContent =
      'updated ' + new Date().toLocaleTimeString();

    if (list.length === 0) {
      el.innerHTML = '<div class="text-muted text-xs font-mono">Collecting data… (first sample takes ~15s)</div>';
      return;
    }

    const maxW = list[0].est_w !== null && list[0].est_w !== undefined ? list[0].est_w : 1;

    el.innerHTML = list.map((p, i) => {
      const hasW   = p.est_w !== null && p.est_w !== undefined;
      const maxVal = hasW ? maxW : 1;
      const barPct = Math.max(2, ((hasW ? p.est_w : p.cpu_pct / 100) / maxVal) * 100);
      const wStr   = hasW
        ? (p.est_w >= 0.1 ? `${p.est_w.toFixed(2)} W` : `${(p.est_w * 1000).toFixed(0)} mW`)
        : null;
      const cpuStr  = `${p.cpu_pct.toFixed(1)}%`;
      const rightLabel = wStr ? `${cpuStr} · ${wStr}` : cpuStr;
      // color: top process gets accent, rest fade
      const opacity = Math.max(0.35, 1 - i * 0.07);
      return `
      <div class="flex items-center gap-3 py-1.5 border-b border-border last:border-0">
        <div class="font-mono text-xs text-muted w-6 text-right flex-shrink-0">${i + 1}</div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between mb-1">
            <span class="font-mono text-xs text-text truncate" title="${p.name} (pid ${p.pid})">${p.name}</span>
            <span class="font-mono text-xs text-label flex-shrink-0 ml-2">${rightLabel}</span>
          </div>
          <div class="h-1 rounded-full bg-border overflow-hidden">
            <div class="h-full rounded-full transition-all duration-500"
                 style="width:${barPct}%; background: rgba(91,156,246,${opacity})"></div>
          </div>
        </div>
      </div>`;
    }).join('');
  } catch(e) {
    console.error(e);
  }
}
</script>
</body>
</html>
"""
