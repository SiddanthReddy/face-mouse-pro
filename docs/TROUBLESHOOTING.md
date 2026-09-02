# Face Mouse Pro — Troubleshooting & Diagnostics Guide

## 🔍 Diagnostic Checklist

### 1. Camera Issues

#### "Could not open camera device index 0"
- **Cause**: Another application (Zoom, Teams, Discord, browser) has exclusive access to the webcam.
- **Fix**:
  1. Close any application using the camera.
  2. Open `config/settings.json` and change `"device_index": 0` to `1` or `2` if using an external USB webcam.
  3. Reconnect the USB webcam.

#### Low Frame Rate (< 20 FPS)
- **Cause**: Camera defaulting to unoptimized exposure mode or USB 2.0 bandwidth saturation.
- **Fix**:
  1. Ensure adequate room lighting (low light forces cameras to drop FPS for exposure).
  2. Verify resolution in `config/settings.json` is set to `640x480`.

---

### 2. Gesture Recognition Tuning

#### Left Clicks Not Triggering
- Look at the **L-EYE** meter in the bottom-left of the camera window:
  - When eye is **OPEN**, EAR should be ~`0.28 - 0.35`.
  - When eye is **CLOSED**, EAR should drop below the red threshold tick line (~`0.10 - 0.18`).
  - If EAR stays above `0.21` when closed, press **'O'** and adjust **Blink EAR Threshold** to `0.24` or `0.26`.

#### Accidental Clicks During Normal Blinking
- **Cause**: One eye closing slightly faster than the other during natural blinks.
- **Fix**: Increase `blink_min_frames` in `config/settings.json` from `2` to `3` or `4`.

---

### 3. Cursor Motion Tuning

#### Cursor Jitters While Staring at One Point
- **Fix**: Press **'O'** to open the Settings GUI and increase **Motion Deadzone** (e.g. from `0.008` to `0.015`).

#### Cursor Moves Too Slowly or Too Fast
- **Fix**: Use keyboard keys **`S`** (faster) or **`D`** (slower), or open the Settings Panel to adjust **X/Y Sensitivity**.
