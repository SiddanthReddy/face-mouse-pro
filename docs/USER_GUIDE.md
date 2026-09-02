# Face Mouse Pro — User Guide & Manual

## 1. Quick Start

1. **Launch the Application**:
   Run `FaceMousePro.exe` or execute `python main.py`.
2. **Position Your Face**:
   Ensure your face is clearly visible inside the camera feed.
3. **Calibrate Neutral Position**:
   Look comfortably straight ahead at the center of your screen and press **SPACE**.
4. **Start Controlling**:
   Tilt or turn your head slightly in any direction to glide the cursor across the screen.

---

## 2. Gesture Controls Reference

| Gesture | Action | Description |
| :--- | :--- | :--- |
| **Head Tilt / Movement** | **Move Cursor** | Smooth, real-time mouse movement relative to your calibrated neutral head pose. |
| **Left Eye Blink (Single)** | **Left Click** | Close your left eye briefly and open it to perform a standard left click. |
| **Left Eye Rapid Double Blink** | **Double Click** | Blink your left eye twice in rapid succession (< 0.40s) to double-click. |
| **Right Eye Blink** | **Right Click** | Close your right eye briefly and open it to open context menus. |
| **Long Left Eye Blink (>0.8s)**| **Drag & Drop Toggle** | Hold your left eye closed for 0.8s to engage mouse drag. Hold again to release. |
| **Mouth Open + Head Pitch** | **Scroll Up / Down** | Open your mouth slightly: tilt head UP to scroll up, or tilt head DOWN to scroll down. |
| **Natural Both-Eye Blink** | *Ignored* | Involuntary natural blinking with both eyes is filtered out automatically. |

---

## 3. Keyboard Shortcuts

| Key | Function |
| :--- | :--- |
| **SPACE** | Calibrate / Set current head position as neutral center |
| **P** | Pause / Resume face tracking and mouse control |
| **S** | Increase cursor sensitivity (+0.2) |
| **D** | Decrease cursor sensitivity (-0.2) |
| **R** | Reset calibration state |
| **Q / ESC** | Safely shut down Face Mouse Pro |

---

## 4. Customizing Settings

All parameters can be tuned in `config/settings.json`:

```json
{
    "cursor": {
        "sensitivity_x": 2.2,
        "sensitivity_y": 2.0,
        "smoothing_factor": 0.65,
        "deadzone_x": 0.008,
        "deadzone_y": 0.008,
        "acceleration_curve": 1.2
    },
    "gestures": {
        "blink_ear_threshold": 0.21,
        "double_click_window_sec": 0.40,
        "long_blink_duration_sec": 0.80,
        "mouth_mar_threshold": 0.45
    },
    "scroll": {
        "scroll_speed": 30
    }
}
```

---

## 5. Troubleshooting & Tips

- **Cursor Jitters**: Increase `deadzone_x` and `deadzone_y` in `config/settings.json`.
- **Clicks Not Triggering**: Check the on-screen EAR meter bar at the bottom-left. Ensure that when you close an eye, the cyan bar dips below the red threshold line. If needed, slightly raise `blink_ear_threshold` (e.g. from 0.21 to 0.24).
- **Webcam Lighting**: Ensure even frontal lighting on your face for optimal landmark tracking.
