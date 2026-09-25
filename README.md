# Dioptase Burst

Full-colour neon **asteroids-burst** arcade for [ElbowOS](https://x.com/ElbowOS). Original **Python 3 + pygame** ship: steer a dioptase wedge, punch gold bolts through teal crystal clusters, chain splits for combos.

Not a clone of prior ElbowOS packs (light-cycle, gear-ride, letter-rain, pinball, tide-hopper, etc.).

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 dioptase_burst.py --play
```

- **A / D** or ← → — turn
- **W** or ↑ — thrust
- **Space** / **K** — fire
- **R** — reset
- **Esc** — quit

Needs Python 3.10+ and a desktop window (pygame + SDL).

## Record a 15s autoplay reel

```bash
ELBOWOS_RECORD=1 python3 dioptase_burst.py
# or
python3 dioptase_burst.py --record
```

Writes a 1080×1920 H.264 MP4 (15s @ 30fps) via ffmpeg. Default path: `/home/workdir/artifacts/DIOPTASE_BURST_ElbowOS.mp4`. Override with `ELBOWOS_MP4`.

## Links

- Reel on Drive: https://drive.google.com/file/d/1G0QHg_XpHiapN_Vqtzsq812yziO0naRc/view
- ElbowOS: https://x.com/ElbowOS
- This repo: https://github.com/ApacheAde/elbowos-dioptase-burst
