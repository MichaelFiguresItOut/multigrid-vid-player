"""
Local Multi‑Video Grid Player
Run:  python multi_video_grid_player.py
Then open: http://127.0.0.1:5000

IMPORTANT BEHAVIOR:
- The grid fills the entire screen
- Each video maintains its aspect ratio (no cropping)
- Videos are as large as possible while fitting in the grid
- No scrolling is possible
- No gaps between videos
"""

import os

from flask import Flask, render_template_string

app = Flask(__name__)

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Multi Video Grid Player</title>
<style>
  /* ===== NEVER ALLOW SCROLLING ===== */
  html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    background: black;
    overflow: hidden; /* <---- THIS PREVENTS SCROLLING */
    font-family: system-ui, sans-serif;
  }

  /* ===== FULL SCREEN CONTAINERS ===== */
  #optionsScreen, #playbackScreen {
    position: fixed;
    inset: 0;
    width: 100vw;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: black;
  }

  #optionsScreen {
    flex-direction: row;
    gap: 12px;
    padding: 16px;
    color: #eee;
    align-items: flex-start;
  }
  
  #leftPanel {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  #keyGuide {
    width: 280px;
    padding: 12px;
    background: #222;
    border: 1px solid #444;
    border-radius: 6px;
    font-size: 12px;
  }
  
  #keyGuide h3 {
    margin: 0 0 8px 0;
    font-size: 14px;
  }
  
  #keyGuide .guide-grid {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 6px 12px;
  }
  
  #keyGuide strong {
    color: #0af;
  }
  
  /* Floating key guide during playback */
  #playbackKeyGuide {
    position: fixed;
    top: 20px;
    right: 20px;
    width: 280px;
    padding: 12px;
    background: rgba(34, 34, 34, 0.95);
    border: 1px solid #444;
    border-radius: 6px;
    font-size: 12px;
    color: #eee;
    display: none;
    z-index: 1000;
  }
  
  #playbackKeyGuide h3 {
    margin: 0 0 8px 0;
    font-size: 14px;
  }
  
  #playbackKeyGuide .guide-grid {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 6px 12px;
  }
  
  #playbackKeyGuide strong {
    color: #0af;
  }

  /* PLAYBACK SCREEN FILLS ENTIRE VIEWPORT */
  #playbackScreen {
    padding: 0;
    margin: 0;
  }

  /* GRID FILLS THE ENTIRE SCREEN */
  #videoGrid {
    width: 100vw;
    height: 100vh;
    display: grid;
    background: black;
    overflow: hidden;
    grid-auto-rows: 1fr;
    grid-auto-columns: 1fr;
    gap: 0; /* NO GAPS BETWEEN VIDEOS */
  }

  /* EACH VIDEO MAINTAINS ASPECT RATIO */
  video {
    width: 100%;
    height: 100%;
    min-width: 0;   /* IMPORTANT: allow grid to shrink item */
    min-height: 0;  /* IMPORTANT: allow grid to shrink item */
    object-fit: contain; /* MAINTAIN ASPECT RATIO, NO CROPPING */
    background: black;
    display: block; /* remove any inline spacing */
  }

  /* ===== OPTIONS UI ===== */
  .controls { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
  button { background: #333; color: #eee; border: 1px solid #555; padding: 8px 12px; cursor: pointer; border-radius: 6px; }
  button:hover { background: #444; }
  input[type=number] { width: 60px; background: #222; color: #eee; border: 1px solid #555; padding: 4px; }
  input[type=color] { width: 50px; height: 30px; background: #222; border: 1px solid #555; cursor: pointer; }

  #gridPreview {
    flex: 1;
    width: 100%;
    display: grid;
    gap: 6px;
    background: #000;
    padding: 6px;
    border: 1px solid #333;
  }

  .cell {
    border: 1px dashed #444;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; text-align: center; padding: 4px; background: #111; color: #aaa;
  }

  .cell.dragover { outline: 2px solid #0af; }
  .cell.selected { outline: 2px solid #0f0; background: #133; }
  .cell:hover { background: #222; cursor: pointer; }
</style>
</head>
<body>

<!-- ================= OPTIONS SCREEN ================= -->
<div id="optionsScreen">
  <div id="leftPanel">
    <h2>Multi Video Grid Player — Setup</h2>

    <div class="controls">
      <button id="addVideosBtn">Add Videos</button>
      <input id="fileInput" type="file" accept="video/mp4" multiple hidden />

      <label>Rows: <input id="rowsInput" type="number" min="1" max="5" value="2" /></label>
      <label>Cols: <input id="colsInput" type="number" min="1" max="5" value="2" /></label>
      
      <label>Speed: <input id="speedInput" type="number" min="0.25" max="4" step="0.25" value="1" style="width: 70px;" />x</label>
      
      <label>Grid Line Thickness: <input id="gapInput" type="number" min="0" max="20" value="0" style="width: 60px;" />px</label>
      <label>Grid Line Color: <input id="gapColorInput" type="color" value="#000000" /></label>

      <button id="clearBtn">Clear All</button>
      <button id="startBtn">Start Playback</button>
    </div>

    <div id="gridPreview"></div>
  </div>

  <div id="keyGuide">
    <h3>Keyboard Controls</h3>
    <div class="guide-grid">
      <strong>Space</strong><span>Pause/Unpause</span>
      <strong>P</strong><span>Play all</span>
      <strong>S</strong><span>Stop all</span>
      <strong>Enter</strong><span>Play all (looping)</span>
      <strong>L</strong><span>Speed +0.25x</span>
      <strong>J</strong><span>Speed -0.25x</span>
      <strong>K</strong><span>Reset speed to 1x</span>
      <strong>G</strong><span>Toggle this guide</span>
      <strong>Esc</strong><span>Exit playback</span>
    </div>
  </div>
</div>

<!-- ================= PLAYBACK SCREEN ================= -->
<div id="playbackScreen" style="display:none;">
  <div id="videoGrid"></div>
  
  <div id="playbackKeyGuide">
    <h3>Keyboard Controls</h3>
    <div class="guide-grid">
      <strong>Space</strong><span>Pause/Unpause</span>
      <strong>P</strong><span>Play all</span>
      <strong>S</strong><span>Stop all</span>
      <strong>Enter</strong><span>Play all (looping)</span>
      <strong>L</strong><span>Speed +0.25x</span>
      <strong>J</strong><span>Speed -0.25x</span>
      <strong>K</strong><span>Reset speed to 1x</span>
      <strong>G</strong><span>Toggle this guide</span>
      <strong>Esc</strong><span>Exit playback</span>
    </div>
  </div>
</div>

<script>
let videos = []; // {file, url, name}
let rows = 2, cols = 2;
let playbackRate = 1.0;
let availableVideos = []; // pool of all loaded videos
let selectedCell = null; // currently selected cell for assignment
let gridGap = 0; // thickness of lines between grid boxes
let gridGapColor = '#000000'; // color of lines between grid boxes
let loopEnabled = false; // whether videos should loop

const addBtn = document.getElementById('addVideosBtn');
const fileInput = document.getElementById('fileInput');
const rowsInput = document.getElementById('rowsInput');
const colsInput = document.getElementById('colsInput');
const speedInput = document.getElementById('speedInput');
const gapInput = document.getElementById('gapInput');
const gapColorInput = document.getElementById('gapColorInput');
const clearBtn = document.getElementById('clearBtn');
const gridPreview = document.getElementById('gridPreview');
const startBtn = document.getElementById('startBtn');
const playbackKeyGuide = document.getElementById('playbackKeyGuide');

const optionsScreen = document.getElementById('optionsScreen');
const playbackScreen = document.getElementById('playbackScreen');
const videoGrid = document.getElementById('videoGrid');

addBtn.onclick = () => fileInput.click();

fileInput.onchange = (e) => {
  const newVideos = [];
  for (const file of e.target.files) {
    const url = URL.createObjectURL(file);
    newVideos.push({ file, url, name: file.name });
    availableVideos.push({ file, url, name: file.name });
  }
  fileInput.value = '';
  
  // If a cell is selected, assign the first new video to it
  if (selectedCell !== null && newVideos.length > 0) {
    videos[selectedCell] = newVideos[0];
    selectedCell = null;
    // Add remaining videos to next available slots
    for (let i = 1; i < newVideos.length; i++) {
      const nextEmpty = videos.findIndex((v, idx) => !v);
      if (nextEmpty !== -1) {
        videos[nextEmpty] = newVideos[i];
      } else {
        videos.push(newVideos[i]);
      }
    }
  } else {
    // No cell selected - add videos to next available slots
    for (const video of newVideos) {
      const nextEmpty = videos.findIndex(v => !v);
      if (nextEmpty !== -1) {
        videos[nextEmpty] = video;
      } else {
        videos.push(video);
      }
    }
  }
  
  renderPreview();
};

rowsInput.oninput = () => { rows = clamp(+rowsInput.value,1,5); rowsInput.value = rows; renderPreview(); };
colsInput.oninput = () => { cols = clamp(+colsInput.value,1,5); colsInput.value = cols; renderPreview(); };
speedInput.oninput = () => { playbackRate = clamp(+speedInput.value, 0.25, 4); speedInput.value = playbackRate; };
gapInput.oninput = () => { gridGap = clamp(+gapInput.value, 0, 20); gapInput.value = gridGap; };
gapColorInput.oninput = () => { gridGapColor = gapColorInput.value; };

clearBtn.onclick = () => {
  videos = [];
  availableVideos = [];
  selectedCell = null;
  renderPreview();
};

function clamp(v,min,max){ return Math.max(min,Math.min(max,v)); }

/* ===== PREVIEW GRID (OPTIONS SCREEN) ===== */
function renderPreview() {
  const slots = rows * cols;
  gridPreview.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
  gridPreview.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
  gridPreview.innerHTML = '';

  for (let i = 0; i < slots; i++) {
    const cell = document.createElement('div');
    cell.className = 'cell';
    cell.dataset.index = i;
    cell.draggable = true;

    if (videos[i]) {
      cell.textContent = videos[i].name;
    } else {
      cell.textContent = '(empty)';
    }
    
    if (selectedCell === i) {
      cell.classList.add('selected');
    }

    // Click to select cell for video assignment
    cell.onclick = () => {
      selectedCell = i;
      renderPreview();
      fileInput.click();
    };

    cell.ondragstart = e => e.dataTransfer.setData('text/plain', i);
    cell.ondragover = e => { e.preventDefault(); cell.classList.add('dragover'); };
    cell.ondragleave = () => cell.classList.remove('dragover');
    cell.ondrop = e => {
      e.preventDefault(); cell.classList.remove('dragover');
      const from = +e.dataTransfer.getData('text/plain');
      const to = i;
      const tmp = videos[from];
      videos[from] = videos[to];
      videos[to] = tmp;
      renderPreview();
    };

    gridPreview.appendChild(cell);
  }
}

startBtn.onclick = () => startPlayback();

/* ===== PLAYBACK GRID ===== */
function startPlayback() {
  optionsScreen.style.display = 'none';
  playbackScreen.style.display = 'flex';
  document.documentElement.requestFullscreen?.();

  const slots = rows * cols;
  videoGrid.innerHTML = '';

  /* GRID DIVIDES THE ENTIRE SCREEN */
  videoGrid.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
  videoGrid.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
  videoGrid.style.gap = `${gridGap}px`;
  videoGrid.style.background = gridGapColor;

  for (let i = 0; i < slots; i++) {
    if (!videos[i]) continue;
    const v = document.createElement('video');
    v.src = videos[i].url;
    v.preload = 'auto';
    v.playsInline = true;
    v.playbackRate = playbackRate;
    v.loop = false;
    videoGrid.appendChild(v);
  }
}

function getAllVideos(){ return Array.from(document.querySelectorAll('#videoGrid video')); }

function playAll(){ 
  getAllVideos().forEach(v=>{
    v.loop = false;
    v.play();
  });
}
function pauseAll(){ getAllVideos().forEach(v=>v.pause()); }
function togglePause(){
  const vids = getAllVideos();
  if (vids.length === 0) return;
  const isPaused = vids[0].paused;
  if (isPaused) playAll();
  else pauseAll();
}
function stopAll(){ 
  getAllVideos().forEach(v=>{ 
    v.pause(); 
    v.currentTime = 0;
    v.loop = false;
  }); 
}
function playAllWithLoop(){
  getAllVideos().forEach(v=>{
    v.loop = true;
    v.currentTime = 0;
    v.play();
  });
}
function setRate(delta){
  playbackRate = clamp(playbackRate + delta, 0.25, 4.0);
  speedInput.value = playbackRate; // Update the speed indicator
  getAllVideos().forEach(v=>v.playbackRate = playbackRate);
}

function resetRate(){
  playbackRate = 1.0;
  speedInput.value = playbackRate;
  getAllVideos().forEach(v=>v.playbackRate = playbackRate);
}

function exitPlayback(){
  stopAll();
  playbackScreen.style.display = 'none';
  optionsScreen.style.display = 'flex';
  playbackKeyGuide.style.display = 'none';
  document.exitFullscreen?.();
}

function toggleKeyGuide(){
  if (playbackKeyGuide.style.display === 'none' || playbackKeyGuide.style.display === '') {
    playbackKeyGuide.style.display = 'block';
  } else {
    playbackKeyGuide.style.display = 'none';
  }
}

/* ===== KEYBOARD CONTROLS ===== */
window.addEventListener('keydown', (e) => {
  if (playbackScreen.style.display !== 'flex') return;

  if (e.key === ' ' || e.key === 'Spacebar') { e.preventDefault(); togglePause(); }
  if (e.key === 'p' || e.key === 'P') playAll();
  if (e.key === 's' || e.key === 'S') stopAll();
  if (e.key === 'Enter') { e.preventDefault(); playAllWithLoop(); }
  if (e.key === 'l' || e.key === 'L') setRate(+0.25);
  if (e.key === 'j' || e.key === 'J') setRate(-0.25);
  if (e.key === 'k' || e.key === 'K') resetRate();
  if (e.key === 'g' || e.key === 'G') toggleKeyGuide();
  if (e.key === 'Escape') exitPlayback();
});

// Sync input values with variables on page load (in case browser remembered previous values)
rows = clamp(+rowsInput.value, 1, 5);
cols = clamp(+colsInput.value, 1, 5);
playbackRate = clamp(+speedInput.value, 0.25, 4);
gridGap = clamp(+gapInput.value, 0, 20);
gridGapColor = gapColorInput.value;

// Initialize grid preview on page load
renderPreview();
</script>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)


if __name__ == "__main__":
    # Render injects PORT; default to 5000 for local runs
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)