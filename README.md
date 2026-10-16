# Multi Grid Video Player

A full-screen multi-video grid player for comparing multiple videos side by side —
built for YouTube video production workflows where you need to watch several clips
at the same time on the same screen.

React port of an original Python Flask app. No Python or server is required: 
it runs entirely in your browser and plays local MP4 files via object
URLs, so nothing is uploaded anywhere.

## Features

- Grid up to 5×5 (rows × cols) that fills the entire screen — no scrolling, no gaps by default
- Each video maintains its aspect ratio (`object-fit: contain`, no cropping) and is as large as possible within its cell
- Adjustable grid line thickness (0–20 px) and color between cells
- Drag & drop videos between preview cells, or click a cell to assign the next file you add to it
- Playback speed from 0.25x to 4x

## Keyboard controls (during playback)

| Key     | Action                    |
| ------- | ------------------------- |
| Space   | Pause / unpause all       |
| P       | Play all                  |
| S       | Stop all (back to start)  |
| Enter   | Play all (looping)        |
| L       | Speed +0.25x              |
| J       | Speed −0.25x              |
| K       | Reset speed to 1x         |
| G       | Toggle the key guide      |
| Esc     | Exit playback             |

## Local development

```bash
npm install
npm run dev
# then open http://localhost:8080
```

## Production build

```bash
npm run build
npm run preview
```
