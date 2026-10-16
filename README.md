# Multi Video Grid Player

Play multiple MP4 videos in a full-screen grid — built for making YouTube videos that compare different clips on the same screen. Single-file Flask app (the original `claudegridv14.py`), deployed to [Render](https://render.com).

## Features

- **Options screen** — add MP4s, choose rows/cols (1–5), playback speed (0.25–4x in 0.25 steps), grid line thickness (0–20px) and color
- **Grid preview** — click a cell to assign it the next video; drag & drop cells to swap videos
- **Fullscreen playback** — grid fills the entire screen, no scrolling, each video keeps its aspect ratio (`object-fit: contain`)

## Keyboard controls (during playback)

| Key | Action |
| --- | --- |
| `Space` | Pause / unpause all |
| `P` | Play all |
| `S` | Stop all (reset to start) |
| `Enter` | Play all, looping |
| `L` | Speed +0.25x |
| `J` | Speed −0.25x |
| `K` | Reset speed to 1x |
| `G` | Toggle floating key guide (starts hidden) |
| `Esc` | Exit playback back to options |

## Run locally

```bash
pip install -r requirements.txt
python claudegridv14.py
# open http://127.0.0.1:5000
```

The server binds to `$PORT` if set (Render injects it), otherwise 5000.

## Deploy on Render

**Option A — Blueprint (recommended):** in the [Render dashboard](https://dashboard.render.com), click **New → Blueprint**, select this repository (`multigrid-vid-player`). The `render.yaml` at the repo root defines a free web service:

```yaml
services:
  - type: web
    name: multigrid-vid-player
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python claudegridv14.py
    healthCheckPath: /
```

**Option B — manual:** **New → Web Service**, connect this repo, then set:

- Runtime: **Python**
- Build Command: `pip install -r requirements.txt`
- Start Command: `python claudegridv14.py`
- Health Check Path: `/`

The free plan spins the service down after ~15 minutes of inactivity; the first request after that takes a few seconds to wake up.

## Notes

- Videos are loaded from your own device via the file picker and played with object URLs — nothing is uploaded or stored server-side, so it works fine on a stateless Render instance.
- The only change vs. the original script: `app.run` now reads `$PORT` (default 5000) and binds to `0.0.0.0`, which Render requires.
