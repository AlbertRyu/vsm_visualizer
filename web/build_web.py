#!/usr/bin/env python3
"""Build self-contained vsm_visualizer.html with Plotly.js inlined."""

import pathlib
import urllib.request

PLOTLY_URL = "https://cdn.plot.ly/plotly-2.35.2.min.js"
OUT = pathlib.Path(__file__).parent.parent / "vsm_visualizer.html"

APP_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VSM Visualizer</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #ffffff; --bg-panel: #fafafa; --bg-header: #f0f0f0;
  --bg-btn: #e0e0e0; --bg-btn-hover: #cacaca;
  --fg: #222222; --fg-dim: #666666; --border: #dddddd;
  --row-hover: #f0f4ff; --row-selected: #dce8ff;
}
body.dark {
  --bg: #1e1e1e; --bg-panel: #252526; --bg-header: #2d2d2d;
  --bg-btn: #3c3c3c; --bg-btn-hover: #505050;
  --fg: #cccccc; --fg-dim: #888888; --border: #444444;
  --row-hover: #2a2d3a; --row-selected: #1a3a5c;
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
  gap: 8px;
  padding: 8px 12px;
  background: var(--bg-header);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
#dir-label {
  flex: 1;
  color: var(--fg-dim);
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

#main { display: flex; flex: 1; overflow: hidden; }

#left {
  width: 380px;
  min-width: 240px;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border);
  background: var(--bg-panel);
  flex-shrink: 0;
}
#right { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
#right-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

#table-wrap { flex: 1; overflow-y: auto; }

table { width: 100%; border-collapse: collapse; table-layout: fixed; }
col.c-size { width: 58px; }
col.c-mode { width: 82px; }
col.c-sel  { width: 32px; }

th {
  background: var(--bg-header);
  padding: 5px 8px;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 1;
}
td {
  padding: 4px 8px;
  border-bottom: 1px solid var(--border);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
tr:hover td { background: var(--row-hover); }
tr.selected td { background: var(--row-selected); }

.mode-group { display: flex; gap: 6px; align-items: center; font-size: 12px; }
.mode-group label { display: flex; align-items: center; gap: 2px; cursor: pointer; }

#status {
  padding: 5px 10px;
  font-size: 12px;
  color: var(--fg-dim);
  border-top: 1px solid var(--border);
  min-height: 26px;
  flex-shrink: 0;
}

#plot { flex: 1; }

button {
  padding: 5px 12px;
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  background: var(--bg-btn);
  color: var(--fg);
  border: 1px solid var(--border);
  border-radius: 4px;
  white-space: nowrap;
}
button:hover { background: var(--bg-btn-hover); }
button:active { opacity: 0.8; }
</style>
</head>
<body>

<div id="toolbar">
  <button id="btn-open">Open Folder</button>
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

  <div id="right">
    <div id="right-toolbar">
      <button id="btn-plot" disabled>Render Selected</button>
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
  setStatus('Scanning…');

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
  setStatus('Detected ' + state.files.length + ' data file' + (state.files.length !== 1 ? 's' : '') + '.');
}

// ── Render table ───────────────────────────────────────────────────────────
function renderTable() {
  tbody.innerHTML = '';
  state.files.forEach(function(f) {
    const tr = document.createElement('tr');
    tr.dataset.path = f.path;

    const tdName = document.createElement('td');
    tdName.title = f.path;
    tdName.textContent = f.path;
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
    setStatus('Error: mixed modes (MT & MH). Select files of the same mode.');
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
    margin: { l: 65, r: 20, t: 20, b: 55 },
    xaxis: { title: mode === 'MT' ? 'Temperature (K)' : 'Magnetic Field (Oe)', gridcolor: grid, linecolor: grid },
    yaxis: { title: 'Moment (emu)', gridcolor: grid, linecolor: grid },
    legend: { x: 1, xanchor: 'right', y: 1 },
    hovermode: 'closest',
  }, { responsive: true });

  setStatus('Plotted ' + paths.length + ' file' + (paths.length !== 1 ? 's' : '') + ' (' + mode + ' mode).');
}

function setStatus(msg) { statusEl.textContent = msg; }
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

    html = APP_HTML.replace("__PLOTLY_JS__", plotly_js)
    OUT.write_text(html, encoding="utf-8")
    size_mb = OUT.stat().st_size / 1024 / 1024
    print(f"Built {OUT.name} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
