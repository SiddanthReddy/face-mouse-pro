# Changelog

All notable changes to **Face Mouse Pro** will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- Extract platform-independent gesture, calibration, cursor mapping, and smoothing logic into the separately versioned `face-mouse-pro-core` package.
- Add Windows compatibility adapters and pin the shared core to commit `7ae514e29578f09a819ae4f5bb84218049e338e5`.
- Add adapter regression tests, Windows OpenCV dependency validation, and PyInstaller collection for the shared core.
- Update CI to run quality checks, automated tests, dependency validation, and a Windows build. Hardware testing remains a manual release check.

## [1.0.0] - 2026-09-01
### Added
- Real-time MediaPipe Face Mesh tracking with 478 3D facial landmarks.
- 2D One-Euro adaptive kinematic filter for smooth, jitter-free cursor tracking.
- Stateful Eye Aspect Ratio (EAR) gesture engine for Left Click, Right Click, Double Click, and Drag & Drop.
- Dual-eye synchronization filter for involuntary natural blink suppression.
- Mouth Aspect Ratio (MAR) open detector with head pitch scroll mode.
- Spacebar zero-point neutral calibration system with deadzone stabilization.
- Modern CustomTkinter dark-mode Settings Control Panel with live parameter tuning.
- High-visibility OpenCV HUD overlay with real-time EAR/MAR metric gauges and status badges.
- Comprehensive pytest test suite (19 unit tests passing).
- Automated performance benchmarking suite across 480p, 720p, and 1080p resolutions.
- PyInstaller standalone Windows executable compilation (`FaceMousePro.exe`).
- Production documentation suite (User Guide, Architecture, Troubleshooting, Accessibility, Deployment).
