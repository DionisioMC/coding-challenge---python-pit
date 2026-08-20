import json

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  body {{ background:#111; color:#eee; font-family:system-ui,sans-serif; text-align:center; }}
  canvas {{ background:#1b1b1b; border:1px solid #333; margin-top:16px; image-rendering:pixelated; }}
  .controls {{ margin-top:12px; }}
  button {{ background:#333; color:#eee; border:1px solid #555; padding:6px 14px; margin:0 4px; border-radius:4px; cursor:pointer; }}
  button:hover {{ background:#444; }}
  #legend span {{ margin:0 10px; font-weight:600; }}
  #turnLabel {{ margin-top:8px; opacity:0.8; }}
</style>
</head>
<body>
<h2>{title}</h2>
<div id="legend"></div>
<canvas id="board" width="{canvas_w}" height="{canvas_h}"></canvas>
<div class="controls">
  <button onclick="stepTo(0)">⏮ Start</button>
  <button onclick="togglePlay()" id="playBtn">▶ Play</button>
  <button onclick="step(-1)">◀ Step</button>
  <button onclick="step(1)">Step ▶</button>
  <button onclick="stepTo(replay.length-1)">End ⏭</button>
</div>
<div id="turnLabel"></div>

<script>
const replay = {replay_json};
const width = {width};
const height = {height};
const cell = {cell_size};

const canvas = document.getElementById('board');
const ctx = canvas.getContext('2d');
let idx = 0;
let playing = false;
let timer = null;

// Colors are chosen by each bot (BOT_COLOR) and travel with the replay data.
const firstSnap = replay[0];
document.getElementById('legend').innerHTML = firstSnap.players.map(
  p => `<span style="color:${{p.color}}">&#9632; ${{p.name}}</span>`
).join('');

function draw() {{
  const snap = replay[idx];
  ctx.fillStyle = '#1b1b1b';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // grid lines
  ctx.strokeStyle = '#262626';
  for (let x = 0; x <= width; x++) {{
    ctx.beginPath(); ctx.moveTo(x*cell, 0); ctx.lineTo(x*cell, height*cell); ctx.stroke();
  }}
  for (let y = 0; y <= height; y++) {{
    ctx.beginPath(); ctx.moveTo(0, y*cell); ctx.lineTo(width*cell, y*cell); ctx.stroke();
  }}

  snap.players.forEach((p) => {{
    const color = p.color;
    ctx.fillStyle = color + (p.alive ? 'aa' : '33');
    p.trail.forEach(([x, y]) => {{
      ctx.fillRect(x*cell+1, y*cell+1, cell-2, cell-2);
    }});
    if (p.alive) {{
      const [hx, hy] = p.pos;
      ctx.fillStyle = color;
      ctx.fillRect(hx*cell, hy*cell, cell, cell);
    }}
  }});

  document.getElementById('turnLabel').textContent =
    `Turn ${{snap.turn}} / ${{replay[replay.length-1].turn}}` +
    (idx === replay.length-1 ? '  —  ' + snap.players.filter(p=>p.alive).map(p=>p.name).join(', ') +
      (snap.players.some(p=>p.alive) ? ' survives!' : ' — draw') : '');
}}

function step(delta) {{
  idx = Math.max(0, Math.min(replay.length - 1, idx + delta));
  draw();
}}
function stepTo(i) {{ idx = i; draw(); }}
function togglePlay() {{
  playing = !playing;
  document.getElementById('playBtn').textContent = playing ? '⏸ Pause' : '▶ Play';
  if (playing) {{
    timer = setInterval(() => {{
      if (idx >= replay.length - 1) {{ togglePlay(); return; }}
      step(1);
    }}, 90);
  }} else {{
    clearInterval(timer);
  }}
}}

draw();
</script>
</body>
</html>
"""


def save_replay_html(game, path, title="Python Pit Arena", cell_size=22):
    html = HTML_TEMPLATE.format(
        title=title,
        canvas_w=game.width * cell_size,
        canvas_h=game.height * cell_size,
        replay_json=json.dumps(game.replay),
        width=game.width,
        height=game.height,
        cell_size=cell_size,
    )
    with open(path, "w") as f:
        f.write(html)
