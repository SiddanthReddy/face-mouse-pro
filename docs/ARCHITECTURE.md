# Face Mouse Pro — System Architecture & Technical Design

## 1. Executive Summary

**Face Mouse Pro** is an accessibility-first human-computer interaction system engineered in Python. It maps facial topology and gestures in real time to operating-system mouse operations without physical contact. The design emphasizes sub-30ms processing latency, non-invasive blink disambiguation (preventing involuntary blink false-positives), adaptive cursor motion smoothing, and modular software boundaries.

---

## 2. End-to-End Pipeline

```
+------------------+     +-------------------+     +-------------------------+
|  Webcam Ingest   | --> | MediaPipe Mesh    | --> | Normalization & Landmark|
| (OpenCV / DSHOW) |     | (478 3D Features) |     | Feature Extraction      |
+------------------+     +-------------------+     +-------------------------+
                                                                |
                                 +------------------------------+------------------------------+
                                 |                                                             |
                                 v                                                             v
                   +---------------------------+                                 +---------------------------+
                   | Calibration & Motion      |                                 | Gesture Recognition       |
                   | Engine                    |                                 | State Machine             |
                   +---------------------------+                                 +---------------------------+
                     - Neutral point offset                                        - Left/Right EAR calculation
                     - Deadzone filtering                                          - MAR Mouth Open detection
                     - Exponential & One-Euro                                      - Involuntary blink filter
                       Adaptive Smoothing                                          - Double-blink buffer
                                 |                                                             |
                                 +------------------------------+------------------------------+
                                                                |
                                                                v
                                                +-------------------------------+
                                                | OS Mouse & Event Execution    |
                                                | (PyAutoGUI + FailSafe Guard)  |
                                                +-------------------------------+
                                                                |
                                                                v
                                                +-------------------------------+
                                                | OpenCV HUD Compositor         |
                                                | (Landmarks, Gauges, Badges)   |
                                                +-------------------------------+
```

---

## 3. Core Subsystems

### 3.1 Face Tracking & Feature Extraction (`src/core/face_tracker.py`)
- Leverages MediaPipe Face Mesh to track 478 3D landmarks at >30 FPS.
- Primary anchor points:
  - **Nose Tip (Landmark 4)**: Serves as the primary spatial coordinate for head-motion vector tracking.
  - **Left Eye (362, 385, 387, 263, 373, 380)**: 6 canonical landmarks for Left Eye Aspect Ratio (EAR).
  - **Right Eye (33, 160, 158, 133, 153, 144)**: 6 canonical landmarks for Right Eye Aspect Ratio (EAR).
  - **Lips / Mouth (61, 0, 13, 291, 14, 17)**: Inner and outer vertical aperture points for Mouth Aspect Ratio (MAR).

### 3.2 Calibration & Motion Engine (`src/core/calibration.py` & `src/utils/helpers.py`)
- **Neutral Rest Pose**: On pressing `SPACE`, the current head position is set as `(x0, y0)`.
- **Differential Motion Vector**: Computes $\Delta x = x - x_0$ and $\Delta y = y - y_0$.
- **Deadzone Filtering**: Ignores involuntary micro-movements when $|\Delta x| < \delta_{deadzone}$ to eliminate resting drift.
- **One-Euro Adaptive Filter**: 
  - Dynamic cutoff frequency: $\omega_c = \omega_{min} + eta |\dot{x}|$
  - Filters high-frequency tremor during static gaze while ensuring zero-lag tracking during fast head turns.

### 3.3 Gesture Recognition Engine (`src/core/gesture_detector.py`)
- **Eye Aspect Ratio (EAR)**:
  $$EAR = rac{||P_2 - P_6|| + ||P_3 - P_5||}{2 ||P_1 - P_4||}$$
- **Mouth Aspect Ratio (MAR)**:
  $$MAR = rac{||P_2 - P_6|| + ||P_3 - P_5||}{2 ||P_1 - P_4||}$$
- **Involuntary Blink Filtering**:
  When both eyes drop below the threshold simultaneously, the frame sequence is recognized as a natural physiological blink and discarded from single-eye click triggers.
- **Gesture State Machine**:
  - `Left Eye Closed (2-14 frames)` $ightarrow$ Pending Left Click (confirmed upon release if double-click timeout expires).
  - `Two Left Eye Blinks (<400ms)` $ightarrow$ Double Click.
  - `Right Eye Closed (2-14 frames)` $ightarrow$ Right Click.
  - `Left Eye Held Closed (>800ms)` $ightarrow$ Drag & Drop Toggle (`mouseDown` / `mouseUp`).
  - `Mouth Open (MAR > 0.45)` $ightarrow$ Scroll Mode (Pitch Up = Scroll Up, Pitch Down = Scroll Down).

### 3.4 OS Mouse Controller (`src/core/mouse_controller.py`)
- Translates smoothed motion vectors into screen coordinate shifts.
- Provides screen border safety margins to eliminate edge locking and avoid corner failsafe locks.
- Manages drag state locks and cleanup routines during shutdown.

### 3.5 HUD Overlay Renderer (`src/ui/overlay.py`)
- Ultra-low overhead OpenCV rasterization:
  - Header banner with active mode (`NORMAL`, `DRAGGING`, `SCROLL MODE`, `PAUSED`).
  - Real-time EAR and MAR gauge bars with threshold indicator lines.
  - Contour polylines around eyes and lips.
  - Nose targeting reticle.
  - FPS counter and sensitivity indicator.
