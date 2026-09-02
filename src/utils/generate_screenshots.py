"""
Programmatic Screenshot & Branding Asset Generator for Face Mouse Pro.
Renders realistic HD (1280x720) screenshot states and logo/icon assets
for documentation and portfolio presentation.
"""

import os
import sys

import cv2
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.ui.overlay import HUDOverlay

SCREENSHOTS_DIR = os.path.join(PROJECT_ROOT, "docs", "screenshots")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)


def create_base_camera_canvas(w: int = 1280, h: int = 720) -> np.ndarray:
    """
    Creates a clean, studio-lit camera background with a stylized human face silhouette.
    """
    img = np.zeros((h, w, 3), dtype=np.uint8)

    # Subtle gradient background
    for y in range(h):
        val = int(22 + (y / h) * 15)
        img[y, :] = (val + 5, val, val + 10)

    # Face silhouette
    cx, cy = w // 2, int(h * 0.48)
    # Head contour
    cv2.ellipse(img, (cx, cy), (int(w * 0.16), int(h * 0.32)), 0, 0, 360, (55, 50, 65), -1, cv2.LINE_AA)
    # Shoulders
    cv2.ellipse(img, (cx, int(h * 0.95)), (int(w * 0.35), int(h * 0.30)), 0, 0, 360, (40, 35, 48), -1, cv2.LINE_AA)

    return img


def get_mock_tracking_data(
    w: int, h: int, is_mouth_open: bool = False, left_closed: bool = False, right_closed: bool = False
):
    cx, cy = w // 2, int(h * 0.46)

    # Nose point
    nose_px = (cx, int(cy + h * 0.03))

    # Eyes points
    l_eye_y_top = cy - int(h * 0.05) if not left_closed else cy - int(h * 0.03)
    l_eye_y_bot = cy - int(h * 0.01) if not left_closed else cy - int(h * 0.03)
    left_eye_px = [
        (cx - int(w * 0.08), cy - int(h * 0.03)),
        (cx - int(w * 0.06), l_eye_y_top),
        (cx - int(w * 0.04), l_eye_y_top),
        (cx - int(w * 0.02), cy - int(h * 0.03)),
        (cx - int(w * 0.04), l_eye_y_bot),
        (cx - int(w * 0.06), l_eye_y_bot),
    ]

    r_eye_y_top = cy - int(h * 0.05) if not right_closed else cy - int(h * 0.03)
    r_eye_y_bot = cy - int(h * 0.01) if not right_closed else cy - int(h * 0.03)
    right_eye_px = [
        (cx + int(w * 0.02), cy - int(h * 0.03)),
        (cx + int(w * 0.04), r_eye_y_top),
        (cx + int(w * 0.06), r_eye_y_top),
        (cx + int(w * 0.08), cy - int(h * 0.03)),
        (cx + int(w * 0.06), r_eye_y_bot),
        (cx + int(w * 0.04), r_eye_y_bot),
    ]

    # Mouth points
    m_y_open = cy + int(h * 0.16) if is_mouth_open else cy + int(h * 0.11)
    mouth_px = [
        (cx - int(w * 0.05), cy + int(h * 0.10)),
        (cx, cy + int(h * 0.08)),
        (cx + int(w * 0.05), cy + int(h * 0.10)),
        (cx + int(w * 0.03), m_y_open),
        (cx, m_y_open),
        (cx - int(w * 0.03), m_y_open),
    ]

    return {
        "nose": (0.5, 0.5),
        "left_eye": [(p[0] / w, p[1] / h) for p in left_eye_px],
        "right_eye": [(p[0] / w, p[1] / h) for p in right_eye_px],
        "mouth": [(p[0] / w, p[1] / h) for p in mouth_px],
        "pixels": {"nose": nose_px, "left_eye": left_eye_px, "right_eye": right_eye_px, "mouth": mouth_px},
    }


def generate_all_screenshots():
    print("Generating comprehensive HD screenshot assets for documentation...")
    hud = HUDOverlay()
    w, h = 1280, 720

    # 1. Main Window
    canvas = create_base_camera_canvas(w, h)
    td = get_mock_tracking_data(w, h)
    img1 = hud.render(canvas, td, 30.0, True, False, False, False, 0.32, 0.31, 0.15, 0.21, 0.45, 2.2)
    cv2.imwrite(os.path.join(SCREENSHOTS_DIR, "01_main_window.png"), img1)

    # 2. Tracking Active
    canvas = create_base_camera_canvas(w, h)
    td = get_mock_tracking_data(w, h)
    img2 = hud.render(canvas, td, 32.4, True, False, False, False, 0.34, 0.33, 0.12, 0.21, 0.45, 2.2)
    cv2.imwrite(os.path.join(SCREENSHOTS_DIR, "02_tracking_active.png"), img2)

    # 3. Calibration Mode
    canvas = create_base_camera_canvas(w, h)
    td = get_mock_tracking_data(w, h)
    img3 = hud.render(canvas, td, 30.0, False, False, False, False, 0.30, 0.30, 0.10, 0.21, 0.45, 2.2)
    cv2.imwrite(os.path.join(SCREENSHOTS_DIR, "03_calibration_mode.png"), img3)

    # 4. Scroll Mode
    canvas = create_base_camera_canvas(w, h)
    td = get_mock_tracking_data(w, h, is_mouth_open=True)
    img4 = hud.render(canvas, td, 31.0, True, False, False, True, 0.29, 0.28, 0.58, 0.21, 0.45, 2.2)
    cv2.imwrite(os.path.join(SCREENSHOTS_DIR, "04_scroll_mode.png"), img4)

    # 5. Drag Mode
    canvas = create_base_camera_canvas(w, h)
    td = get_mock_tracking_data(w, h, left_closed=True)
    img5 = hud.render(canvas, td, 29.8, True, False, True, False, 0.08, 0.32, 0.14, 0.21, 0.45, 2.2)
    cv2.imwrite(os.path.join(SCREENSHOTS_DIR, "05_drag_mode.png"), img5)

    # 6. Settings Panel Showcase
    settings_img = np.zeros((720, 640, 3), dtype=np.uint8)
    settings_img[:] = (15, 23, 42)  # Dark slate
    cv2.rectangle(settings_img, (0, 0), (640, 60), (30, 41, 59), -1)
    cv2.putText(settings_img, "FACE MOUSE PRO - SETTINGS", (25, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 245, 212), 2)
    cv2.putText(
        settings_img, "Cursor Motion & Sensitivity", (25, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (56, 189, 248), 2
    )
    cv2.putText(settings_img, "X Sensitivity: 2.20x", (25, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
    cv2.rectangle(settings_img, (25, 155), (615, 165), (51, 65, 85), -1)
    cv2.rectangle(settings_img, (25, 155), (320, 165), (0, 245, 212), -1)
    cv2.putText(
        settings_img, "Blink EAR Threshold: 0.21", (25, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1
    )
    cv2.rectangle(settings_img, (25, 235), (615, 245), (51, 65, 85), -1)
    cv2.rectangle(settings_img, (25, 235), (280, 245), (0, 245, 212), -1)
    cv2.imwrite(os.path.join(SCREENSHOTS_DIR, "06_settings_panel.png"), settings_img)

    # 7. HUD Gauges Focus
    gauges_crop = img1[h - 120 : h, 0:w]
    cv2.imwrite(os.path.join(SCREENSHOTS_DIR, "07_hud_gauges.png"), gauges_crop)

    # Generate Project Icon / Logo
    logo = np.zeros((256, 256, 3), dtype=np.uint8)
    logo[:] = (15, 23, 42)
    cv2.circle(logo, (128, 128), 110, (0, 245, 212), 4, cv2.LINE_AA)
    cv2.circle(logo, (128, 128), 70, (204, 0, 255), 2, cv2.LINE_AA)
    # Stylized Reticle
    cv2.line(logo, (128, 30), (128, 226), (0, 245, 212), 2, cv2.LINE_AA)
    cv2.line(logo, (30, 128), (226, 128), (0, 245, 212), 2, cv2.LINE_AA)
    cv2.putText(logo, "FMP", (75, 142), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3, cv2.LINE_AA)
    cv2.imwrite(os.path.join(ASSETS_DIR, "icon.png"), logo)
    cv2.imwrite(os.path.join(ASSETS_DIR, "logo.png"), logo)

    print(f"[SUCCESS] All screenshots and logo assets generated in: {SCREENSHOTS_DIR} and {ASSETS_DIR}")


if __name__ == "__main__":
    generate_all_screenshots()
