#!/usr/bin/env python3
"""Build self-contained vsm_visualizer.html with Plotly.js inlined."""

import base64
import pathlib
import urllib.request

PLOTLY_URL = "https://cdn.plot.ly/plotly-2.35.2.min.js"
ICON_PATH = pathlib.Path(__file__).parent.parent / "src/vsm_visualizer/assets/vsm_logo.ico"
OUT = pathlib.Path(__file__).parent.parent / "vsm_visualizer.html"

APP_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VSM Visualizer</title>
<link rel="icon" type="image/x-icon" href="__FAVICON__">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #ffffff; --bg-panel: #f7f7f8; --bg-header: #efefef;
  --bg-btn: #e4e4e7; --bg-btn-hover: #d4d4d8;
  --fg: #18181b; --fg-dim: #71717a; --fg-muted: #a1a1aa;
  --border: #e4e4e7; --border-strong: #d4d4d8;
  --row-hover: #f0f4ff; --row-selected: #dbeafe;
  --accent: #2563eb; --accent-hover: #1d4ed8;
  --accent-fg: #ffffff;
  --radius: 5px;
}
body.dark {
  --bg: #18181b; --bg-panel: #1e1e21; --bg-header: #27272a;
  --bg-btn: #3f3f46; --bg-btn-hover: #52525b;
  --fg: #e4e4e7; --fg-dim: #a1a1aa; --fg-muted: #71717a;
  --border: #3f3f46; --border-strong: #52525b;
  --row-hover: #1e2a3a; --row-selected: #1e3a5f;
  --accent: #3b82f6; --accent-hover: #60a5fa;
  --accent-fg: #ffffff;
}

body {
  font-family: 'Segoe UI', system-ui, Arial, sans-serif;
  font-size: 13px;
  background: var(--bg);
  color: var(--fg);
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

#toolbar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 10px;
  background: var(--bg-header);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
#dir-label {
  flex: 1;
  color: var(--fg-muted);
  font-size: 11.5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 0 4px;
}

#main { display: flex; flex: 1; overflow: hidden; }

#left {
  width: 400px;
  min-width: 260px;
  display: flex;
  flex-direction: column;
  background: var(--bg-panel);
  flex-shrink: 0;
}
#divider {
  width: 5px;
  cursor: col-resize;
  background: var(--border);
  flex-shrink: 0;
  transition: background 0.15s;
}
#divider:hover, #divider.dragging {
  background: var(--border-strong);
}
#right { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
#right-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 10px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  background: var(--bg-header);
}

#table-wrap {
  flex: 1;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--border-strong) transparent;
}
#table-wrap::-webkit-scrollbar { width: 6px; }
#table-wrap::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 3px; }
#table-wrap::-webkit-scrollbar-track { background: transparent; }

table { width: 100%; border-collapse: collapse; table-layout: fixed; }
col.c-size { width: 62px; }
col.c-mode { width: 100px; }
col.c-sel  { width: 34px; }

th {
  background: var(--bg-header);
  padding: 6px 8px;
  text-align: left;
  font-weight: 600;
  font-size: 11.5px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--fg-dim);
  border-bottom: 1px solid var(--border-strong);
  position: sticky;
  top: 0;
  z-index: 1;
}
td {
  padding: 5px 8px;
  border-bottom: 1px solid var(--border);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 12.5px;
}
tr:hover td { background: var(--row-hover); }
tr.selected td { background: var(--row-selected); }
tr.selected td.td-name .fname { color: var(--accent); }

/* file name cell: dim directory, emphasise filename */
.td-name { line-height: 1.35; }
.fdir  { color: var(--fg-muted); font-size: 11px; display: block; }
.fname { color: var(--fg); font-size: 12.5px; }

/* mode radio */
.mode-group { display: flex; gap: 8px; align-items: center; }
.mode-group label {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  cursor: pointer;
  color: var(--fg-dim);
  transition: color 0.1s;
}
.mode-group label:has(input:checked) { color: var(--accent); font-weight: 600; }
.mode-group input[type=radio] { accent-color: var(--accent); cursor: pointer; }

/* select-all / row checkbox */
input[type=checkbox] { accent-color: var(--accent); cursor: pointer; width: 14px; height: 14px; }

#status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px;
  font-size: 11.5px;
  color: var(--fg-dim);
  border-top: 1px solid var(--border);
  min-height: 28px;
  flex-shrink: 0;
  background: var(--bg-header);
}
#status::before {
  content: '';
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--fg-muted);
  flex-shrink: 0;
}
#status.ready::before  { background: #22c55e; }
#status.busy::before   { background: #f59e0b; }
#status.error::before  { background: #ef4444; }

#plot { flex: 1; }

button {
  padding: 5px 11px;
  font-size: 12.5px;
  font-family: inherit;
  cursor: pointer;
  background: var(--bg-btn);
  color: var(--fg);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius);
  white-space: nowrap;
  transition: background 0.12s, border-color 0.12s;
}
button:hover { background: var(--bg-btn-hover); }
button:active { opacity: 0.75; }
button:disabled { opacity: 0.4; cursor: default; }

/* primary button */
button.primary {
  background: var(--accent);
  color: var(--accent-fg);
  border-color: var(--accent);
}
button.primary:hover { background: var(--accent-hover); border-color: var(--accent-hover); }
</style>
</head>
<body>

<div id="toolbar">
  <button id="btn-open" class="primary">Open Folder</button>
  <button id="btn-refresh" disabled>Refresh</button>
  <span id="dir-label">No folder selected</span>
  <button id="btn-theme">Toggle Theme</button>
</div>

<div id="main">
  <div id="left">
    <div id="table-wrap">
      <table id="file-table">
        <colgroup>
          <col><col class="c-size"><col class="c-mode"><col class="c-sel">
        </colgroup>
        <thead>
          <tr>
            <th>Data File</th>
            <th>Size (MB)</th>
            <th>Mode</th>
            <th><input type="checkbox" id="select-all" title="Select all"></th>
          </tr>
        </thead>
        <tbody id="file-tbody"></tbody>
      </table>
    </div>
    <div id="status">Open a folder to begin.</div>
  </div>

  <div id="divider"></div>

  <div id="right">
    <div id="right-toolbar">
      <button id="btn-plot" class="primary" disabled>Render Selected</button>
    </div>
    <div id="plot"></div>
  </div>
</div>

<script>__PLOTLY_JS__</script>
<script>
'use strict';

const state = {
  dirHandle: null,
  files: [],       // { path, handle, df, mode, size }
  selected: new Set(),
  fileModes: {},   // path -> 'MT'|'MH'
  theme: 'light',
};

const btnOpen    = document.getElementById('btn-open');
const btnRefresh = document.getElementById('btn-refresh');
const btnPlot    = document.getElementById('btn-plot');
const btnTheme   = document.getElementById('btn-theme');
const dirLabel   = document.getElementById('dir-label');
const tbody      = document.getElementById('file-tbody');
const statusEl   = document.getElementById('status');
const selectAll  = document.getElementById('select-all');

// ── Theme ──────────────────────────────────────────────────────────────────
btnTheme.addEventListener('click', () => {
  state.theme = state.theme === 'light' ? 'dark' : 'light';
  document.body.classList.toggle('dark', state.theme === 'dark');
  if (state.selected.size) renderPlot();
});

// ── Open folder ────────────────────────────────────────────────────────────
btnOpen.addEventListener('click', async () => {
  if (!window.showDirectoryPicker) {
    setStatus('Error: File System Access API not supported. Use Chrome or Edge.');
    return;
  }
  try {
    state.dirHandle = await window.showDirectoryPicker();
    dirLabel.textContent = state.dirHandle.name;
    btnRefresh.disabled = false;
    await refreshFiles();
  } catch (e) {
    if (e.name !== 'AbortError') setStatus('Error: ' + e.message);
  }
});

btnRefresh.addEventListener('click', refreshFiles);

// ── Walk directory recursively ─────────────────────────────────────────────
async function* walkDir(handle, prefix) {
  prefix = prefix || '';
  for await (const [name, entry] of handle.entries()) {
    const path = prefix ? prefix + '/' + name : name;
    if (entry.kind === 'file' && name.toLowerCase().endsWith('.dat')) {
      yield { path, handle: entry };
    } else if (entry.kind === 'directory') {
      yield* walkDir(entry, path);
    }
  }
}

// ── Parse PPMS .dat ────────────────────────────────────────────────────────
const KEEP = /^(Temperature \(|Magnetic Field \(|Moment \(|M\. Std\. Err\. \()/;

async function parseDat(fileHandle) {
  const file = await fileHandle.getFile();
  const buf = await file.arrayBuffer();
  let text;
  try {
    text = new TextDecoder('utf-8', { fatal: true }).decode(buf);
  } catch (_) {
    text = new TextDecoder('iso-8859-1').decode(buf);
  }

  const lines = text.split(/\r?\n/);
  const di = lines.findIndex(function(l) { return l.trim() === '[Data]'; });
  if (di === -1) return null;

  const headers = lines[di + 1].trim().split(',');
  const df = {};
  headers.forEach(function(h) { if (KEEP.test(h)) df[h] = []; });

  for (let i = di + 2; i < lines.length; i++) {
    const row = lines[i].trim();
    if (!row) continue;
    const vals = row.split(',');
    headers.forEach(function(h, j) {
      if (df[h] !== undefined) df[h].push(parseFloat(vals[j]));
    });
  }
  return df;
}

// ── Detect MT/MH ──────────────────────────────────────────────────────────
function detectMode(df) {
  const T = (df['Temperature (K)'] || []).filter(isFinite);
  const H = (df['Magnetic Field (Oe)'] || []).filter(isFinite);
  if (!T.length || !H.length) return 'MT';
  const span = function(a) { return Math.max.apply(null, a) - Math.min.apply(null, a); };
  return span(H) > span(T) ? 'MH' : 'MT';
}

// ── Smart labels ───────────────────────────────────────────────────────────
function smartLabels(paths) {
  if (paths.length === 1) return [paths[0].replace(/\.dat$/i, '')];
  const parts = paths.map(function(p) { return p.replace(/\.dat$/i, '').split('/'); });
  let prefix = 0;
  const minLen = Math.min.apply(null, parts.map(function(p) { return p.length; }));
  for (let i = 0; i < minLen; i++) {
    if (new Set(parts.map(function(p) { return p[i]; })).size === 1) prefix++;
    else break;
  }
  return parts.map(function(p) {
    const s = p.slice(prefix).join('/');
    return s || p[p.length - 1];
  });
}

// ── Refresh files ──────────────────────────────────────────────────────────
async function refreshFiles() {
  state.files = [];
  state.selected.clear();
  state.fileModes = {};
  selectAll.checked = false;
  tbody.innerHTML = '';
  btnPlot.disabled = true;
  setStatus('Scanning…', 'busy');

  let count = 0;
  for await (const entry of walkDir(state.dirHandle)) {
    const file = await entry.handle.getFile();
    const df = await parseDat(entry.handle);
    if (!df) continue;
    const mode = detectMode(df);
    state.files.push({ path: entry.path, handle: entry.handle, df, mode, size: file.size });
    state.fileModes[entry.path] = mode;
    count++;
    setStatus('Loading… (' + count + ' files found)');
  }

  state.files.sort(function(a, b) {
    return a.path.localeCompare(b.path, undefined, { sensitivity: 'base' });
  });
  renderTable();
  setStatus('Detected ' + state.files.length + ' data file' + (state.files.length !== 1 ? 's' : '') + '.', 'ready');
}

// ── Render table ───────────────────────────────────────────────────────────
function renderTable() {
  tbody.innerHTML = '';
  state.files.forEach(function(f) {
    const tr = document.createElement('tr');
    tr.dataset.path = f.path;

    const tdName = document.createElement('td');
    tdName.className = 'td-name';
    tdName.title = f.path;
    const slash = f.path.lastIndexOf('/');
    if (slash !== -1) {
      const fdir = document.createElement('span');
      fdir.className = 'fdir';
      fdir.textContent = f.path.slice(0, slash + 1);
      tdName.appendChild(fdir);
    }
    const fname = document.createElement('span');
    fname.className = 'fname';
    fname.textContent = f.path.slice(slash + 1);
    tdName.appendChild(fname);
    tr.appendChild(tdName);

    const tdSize = document.createElement('td');
    tdSize.textContent = (f.size / 1024 / 1024).toFixed(2);
    tr.appendChild(tdSize);

    const tdMode = document.createElement('td');
    const grp = document.createElement('div');
    grp.className = 'mode-group';
    ['MT', 'MH'].forEach(function(m) {
      const lbl = document.createElement('label');
      const inp = document.createElement('input');
      inp.type = 'radio';
      inp.name = 'mode-' + f.path;
      inp.value = m;
      inp.checked = state.fileModes[f.path] === m;
      inp.addEventListener('change', function() { state.fileModes[f.path] = m; });
      lbl.appendChild(inp);
      lbl.append(' ' + m);
      grp.appendChild(lbl);
    });
    tdMode.appendChild(grp);
    tr.appendChild(tdMode);

    const tdSel = document.createElement('td');
    tdSel.style.textAlign = 'center';
    const cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.addEventListener('change', function() {
      if (cb.checked) state.selected.add(f.path);
      else state.selected.delete(f.path);
      tr.classList.toggle('selected', cb.checked);
      btnPlot.disabled = state.selected.size === 0;
      syncSelectAll();
    });
    tdSel.appendChild(cb);
    tr.appendChild(tdSel);

    tbody.appendChild(tr);
  });
}

function syncSelectAll() {
  const cbs = Array.from(tbody.querySelectorAll('input[type=checkbox]'));
  const n = cbs.filter(function(c) { return c.checked; }).length;
  selectAll.indeterminate = n > 0 && n < cbs.length;
  selectAll.checked = n === cbs.length && cbs.length > 0;
}

selectAll.addEventListener('change', function() {
  tbody.querySelectorAll('input[type=checkbox]').forEach(function(cb) {
    cb.checked = selectAll.checked;
    cb.dispatchEvent(new Event('change'));
  });
});

// ── Plot ───────────────────────────────────────────────────────────────────
btnPlot.addEventListener('click', renderPlot);

function renderPlot() {
  if (!state.selected.size) return;

  const paths = Array.from(state.selected);
  const modes = new Set(paths.map(function(p) { return state.fileModes[p]; }));

  if (modes.size > 1) {
    setStatus('Error: mixed modes (MT & MH). Select files of the same mode.', 'error');
    return;
  }

  const mode   = Array.from(modes)[0];
  const labels = smartLabels(paths);
  const traces = [];

  paths.forEach(function(p, i) {
    const f = state.files.find(function(f) { return f.path === p; });
    if (!f) return;

    const T = f.df['Temperature (K)'] || [];
    const H = f.df['Magnetic Field (Oe)'] || [];
    const M = f.df['Moment (emu)'] || [];

    const x = [], y = [];
    for (let j = 0; j < M.length; j++) {
      const xv = mode === 'MT' ? T[j] : H[j];
      if (isFinite(xv) && isFinite(M[j])) { x.push(xv); y.push(M[j]); }
    }
    traces.push({ x, y, mode: 'lines', name: labels[i], type: 'scatter' });
  });

  const dark     = state.theme === 'dark';
  const bgColor  = dark ? '#1e1e1e' : '#ffffff';
  const fgColor  = dark ? '#cccccc' : '#222222';
  const grid     = dark ? '#444444' : '#e0e0e0';

  Plotly.react('plot', traces, {
    paper_bgcolor: bgColor,
    plot_bgcolor:  bgColor,
    font: { color: fgColor, family: "'Segoe UI', system-ui, Arial, sans-serif", size: 12 },
    margin: { l: 80, r: 40, t: 40, b: 80 },
    xaxis: { title: { text: mode === 'MT' ? 'Temperature (K)' : 'Magnetic Field (Oe)', standoff: 15 }, gridcolor: grid, linecolor: grid },
    yaxis: { title: { text: 'Moment (emu)', standoff: 15 }, gridcolor: grid, linecolor: grid },
    legend: { x: 1, xanchor: 'right', y: 1 },
    hovermode: 'closest',
  }, { responsive: true, edits: { legendPosition: true } });

  setStatus('Plotted ' + paths.length + ' file' + (paths.length !== 1 ? 's' : '') + ' (' + mode + ' mode).', 'ready');
}

function setStatus(msg, type) {
  statusEl.textContent = msg;
  statusEl.className = type || '';
}

// ── Draggable divider ──────────────────────────────────────────────────────
(function() {
  const divider = document.getElementById('divider');
  const left    = document.getElementById('left');
  let dragging = false, startX = 0, startW = 0;

  divider.addEventListener('mousedown', function(e) {
    dragging = true;
    startX = e.clientX;
    startW = left.offsetWidth;
    divider.classList.add('dragging');
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  });

  document.addEventListener('mousemove', function(e) {
    if (!dragging) return;
    const newW = Math.max(180, Math.min(startW + e.clientX - startX, window.innerWidth - 200));
    left.style.width = newW + 'px';
  });

  document.addEventListener('mouseup', function() {
    if (!dragging) return;
    dragging = false;
    divider.classList.remove('dragging');
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  });
})();
</script>
</body>
</html>
"""


def main():
    print(f"Downloading Plotly.js from {PLOTLY_URL} ...")
    with urllib.request.urlopen(PLOTLY_URL) as r:
        plotly_js = r.read().decode("utf-8")

    # Escape </script> inside the inlined JS to prevent early tag termination
    plotly_js = plotly_js.replace("</script>", r"<\/script>")

    favicon_b64 = base64.b64encode(ICON_PATH.read_bytes()).decode("ascii")
    favicon_uri = f"data:image/x-icon;base64,{favicon_b64}"

    html = APP_HTML.replace("__PLOTLY_JS__", plotly_js).replace("__FAVICON__", favicon_uri)
    OUT.write_text(html, encoding="utf-8")
    size_mb = OUT.stat().st_size / 1024 / 1024
    print(f"Built {OUT.name} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
