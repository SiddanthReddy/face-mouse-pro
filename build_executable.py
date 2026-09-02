"""
Build Runner and Pre-Flight Validation Suite for Face Mouse Pro.
Validates environment integrity and executes PyInstaller with FaceMousePro.spec as the single source of truth.
"""

import json
import os
import subprocess
import sys

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


def run_preflight_validation() -> bool:
    """
    Validates required directory structure, critical files, JSON schemas,
    and runtime dependencies before triggering compilation.
    """
    print("\n[1/4] Running Pre-Flight Validation Checks...")

    # 1. Required Directories
    required_dirs = [
        os.path.join(PROJECT_ROOT, "src"),
        os.path.join(PROJECT_ROOT, "src", "core"),
        os.path.join(PROJECT_ROOT, "src", "ui"),
        os.path.join(PROJECT_ROOT, "src", "utils"),
        os.path.join(PROJECT_ROOT, "src", "config"),
        os.path.join(PROJECT_ROOT, "config"),
        os.path.join(PROJECT_ROOT, "docs"),
        os.path.join(PROJECT_ROOT, "assets"),
        os.path.join(PROJECT_ROOT, "logs"),
    ]

    for d in required_dirs:
        if not os.path.exists(d):
            print(f"  [ERROR] Missing required directory: {d}")
            return False
        print(f"  [OK] Directory verified: {os.path.relpath(d, PROJECT_ROOT)}")

    # 2. Required Files
    required_files = [
        os.path.join(PROJECT_ROOT, "main.py"),
        os.path.join(PROJECT_ROOT, "FaceMousePro.spec"),
        os.path.join(PROJECT_ROOT, "config", "settings.json"),
        os.path.join(PROJECT_ROOT, "requirements.txt"),
        os.path.join(PROJECT_ROOT, "src", "ui", "settings_window.py"),
        os.path.join(PROJECT_ROOT, "src", "core", "face_tracker.py"),
        os.path.join(PROJECT_ROOT, "src", "core", "gesture_detector.py"),
        os.path.join(PROJECT_ROOT, "src", "core", "mouse_controller.py"),
        os.path.join(PROJECT_ROOT, "src", "core", "camera.py"),
        os.path.join(PROJECT_ROOT, "src", "core", "calibration.py"),
    ]

    for f in required_files:
        if not os.path.exists(f):
            print(f"  [ERROR] Missing required file: {f}")
            return False
        print(f"  [OK] File verified: {os.path.relpath(f, PROJECT_ROOT)}")

    # 3. Validate JSON Configuration Schema
    cfg_file = os.path.join(PROJECT_ROOT, "config", "settings.json")
    try:
        with open(cfg_file, encoding="utf-8") as f:
            data = json.load(f)
            required_sections = ["camera", "cursor", "gestures", "scroll", "calibration", "ui"]
            for sec in required_sections:
                if sec not in data:
                    print(f"  [ERROR] Missing required config section '{sec}' in {cfg_file}")
                    return False
        print("  [OK] config/settings.json schema validated successfully.")
    except Exception as e:
        print(f"  [ERROR] Invalid JSON in {cfg_file}: {e}")
        return False

    # 4. Validate Python Dependencies Importable
    print("\n[2/4] Verifying Python Runtime Dependencies...")
    required_modules = ["cv2", "mediapipe", "pyautogui", "numpy", "customtkinter", "PIL", "psutil"]
    for mod in required_modules:
        try:
            __import__(mod)
            print(f"  [OK] Module importable: {mod}")
        except ImportError as e:
            print(f"  [ERROR] Required package '{mod}' is not installed: {e}")
            return False

    return True


def build():
    print("==========================================================")
    print("    Face Mouse Pro — Standalone Executable Build Runner   ")
    print("==========================================================")

    # 1. Pre-Flight Validation
    if not run_preflight_validation():
        print("\n[FATAL] Pre-flight validation failed. Aborting build.")
        sys.exit(1)

    print("\n[3/4] Pre-flight validation passed. Starting PyInstaller with FaceMousePro.spec...")

    spec_file = os.path.join(PROJECT_ROOT, "FaceMousePro.spec")
    dist_dir = os.path.join(PROJECT_ROOT, "dist")

    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", spec_file]

    print(f"Executing: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)

    if result.returncode == 0:
        output_exe = os.path.join(dist_dir, "FaceMousePro", "FaceMousePro.exe")
        print("\n[4/4] Verifying Output Binary...")
        if os.path.exists(output_exe) and os.path.getsize(output_exe) > 0:
            print("==========================================================")
            print(" [SUCCESS] Face Mouse Pro built successfully!")
            print(f" Executable: {output_exe} ({os.path.getsize(output_exe) / (1024 * 1024):.1f} MB)")
            print("==========================================================")
        else:
            print("  [ERROR] Executable binary not found at expected location.")
            sys.exit(1)
    else:
        print("==========================================================")
        print(" [FAILED] Build failed with exit code:", result.returncode)
        print("==========================================================")
        sys.exit(result.returncode)


if __name__ == "__main__":
    build()
