# ✋ Air Mouse — Gesture-Controlled Mouse via Webcam

Control your computer's mouse entirely through hand gestures captured by your webcam — no extra hardware required.

Built with **MediaPipe**, **OpenCV**, and **PyAutoGUI** in Python.

---

## Gestures

| Gesture | Action |
|---------|--------|
| ☝️ Pointing — index finger up | Move cursor |
| 🤘 Metal sign — index + pinky up | Left click |
| ✌️ Peace sign — index + middle up | Right click |
| ✊ Fist — all fingers closed | Scroll |
| ✋ Open hand — all fingers up | Neutral / pause |

---

## How It Works

```
Webcam → OpenCV → MediaPipe HandLandmarker → GestureClassifier → MouseController
```

1. **Capture** — OpenCV reads each frame from the webcam and mirrors it horizontally so the view feels natural.
2. **Detection** — MediaPipe's `HandLandmarker` model identifies 21 hand landmarks in normalized [0, 1] coordinates.
3. **Classification** — `GestureClassifier` applies rule-based logic on the landmark positions (e.g. "index tip above index PIP joint = finger is up"). A 2-frame stability buffer prevents accidental gesture switches caused by hand noise.
4. **Control** — `MouseController` maps the index fingertip position to screen coordinates and moves the cursor. A sensitivity multiplier reduces the required hand movement range, and exponential smoothing eliminates jitter without adding significant lag.

### Cursor Mapping

The hand operates in roughly the **central 40% of the camera frame**. That zone is mapped to the full screen resolution using:

- **Sensitivity amplification** — position is amplified relative to the frame center, so you don't need to sweep your whole arm.
- **Exponential smoothing** — each frame the cursor moves a fraction toward the target: `smooth = smooth + α × (target − smooth)`. This naturally reduces lag for fast movements while smoothing out small noise.

---

## Project Structure

```
air-mouse/
├── main.py                 # Entry point — webcam loop, gesture dispatch
├── hand_tracker.py         # MediaPipe HandLandmarker wrapper
├── gesture_classifier.py   # Rule-based gesture detection with stability buffer
├── mouse_controller.py     # Cursor movement, click, scroll logic
└── requirements.txt
```

---

## Installation

### Requirements

- Python 3.10+
- Webcam
- Linux (X11 or XWayland), macOS, or Windows

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/air-mouse.git
cd air-mouse

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate       # Linux / macOS
# venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

> **Linux only:** PyAutoGUI requires Tkinter. Install it with:
> ```bash
> sudo apt install python3-tk python3-dev
> ```

### First Run

```bash
python3 main.py
```

On the first run, the MediaPipe hand landmark model (~7.5 MB) is downloaded automatically and cached locally. Subsequent runs start instantly.

Press **Q** to quit.

---

## Configuration

All tunable parameters live at the top of their respective files — no config file needed.

### `mouse_controller.py`

| Constant | Default | Description |
|----------|---------|-------------|
| `_SENSITIVITY` | `1.8` | Amplifies hand position relative to frame center. Higher = less arm movement needed to reach screen edges. |
| `_ALPHA` | `0.35` | Exponential smoothing factor. `0.1` = very smooth (more lag), `1.0` = raw (no smoothing). |
| `_MARGIN` | `0.15` | Dead zone at frame edges (fraction of frame). Prevents cursor from being stuck at edges. |
| `_COOLDOWN` | `0.7` | Minimum seconds between clicks. Prevents accidental double-clicks. |

### `gesture_classifier.py`

| Constant | Default | Description |
|----------|---------|-------------|
| `_STABILITY` | `2` | Consecutive frames required to confirm a gesture change. Increase to reduce false triggers. |

---

## Tech Stack

| Library | Version | Role |
|---------|---------|------|
| [MediaPipe](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker) | ≥ 0.10 | 21-point hand landmark detection |
| [OpenCV](https://opencv.org/) | ≥ 4.8 | Webcam capture and frame rendering |
| [PyAutoGUI](https://pyautogui.readthedocs.io/) | ≥ 0.9 | Cross-platform mouse and keyboard control |
| [NumPy](https://numpy.org/) | ≥ 1.24 | Numerical utilities |

---

## Roadmap

- [ ] Drag & drop (hold metal sign + move)
- [ ] Double-click gesture
- [ ] JSON-configurable gesture-to-action mapping
- [ ] Multi-monitor support
- [ ] GUI settings panel
- [ ] macOS / Windows testing

---

## License

MIT License — feel free to use, modify, and distribute.
