# Face Mouse Pro — Production Build & Deployment Guide

## 1. Standalone Executable Compilation

Face Mouse Pro uses **PyInstaller** to bundle Python 3.10+, MediaPipe Face Mesh, OpenCV, PyAutoGUI, and CustomTkinter into a zero-dependency Windows executable.

### Automated Build Command
```powershell
python build_executable.py
```

### Build Artifacts
Upon completion, the distribution directory will be located at:
```
dist/FaceMousePro/
├── FaceMousePro.exe       # Main standalone application
├── _internal/             # Native DLLs, MediaPipe graph models, OpenCV binaries
└── config/                # Persistent user configuration
```

---

## 2. Portable ZIP Distribution Packaging

To generate a clean `.zip` release package:
```powershell
Compress-Archive -Path "dist/FaceMousePro/*" -DestinationPath "dist/FaceMousePro-v1.0.0-Windows-x64.zip" -Force
```

---

## 3. Windows SmartScreen & Antivirus Guidelines
Because PyInstaller bundles native C++ runtime binaries into an executable:
- Windows Defender SmartScreen may display an *"Unrecognized app"* advisory on first run if the executable is not code-signed.
- Click **More Info $ightarrow$ Run Anyway**.
- For production enterprise distribution, sign the binary with a DigiCert or Sectigo EV Code Signing Certificate via `signtool.exe`.
