# Shared core integration (Windows)

The Windows application uses `face_mouse_core` from the separately maintained
[Face Mouse Pro Core repository](https://github.com/SiddanthReddy/face-mouse-pro-core).
The app owns camera capture, MediaPipe/OpenCV, GUI, JSON settings, screen
dimensions, cursor state, PyAutoGUI calls and logging. Compatibility adapters
preserve Windows-facing APIs while delegating platform-independent calculations
to the core.

## Pinned dependency and installation

The app depends on `face-mouse-pro-core==0.1.0`, installed from exact Git commit
`7ae514e29578f09a819ae4f5bb84218049e338e5`. The project uses a `src/` package
layout; pip installs its project metadata and exposes `face_mouse_core` from
that source tree.

Use Python 3.10+ for the Windows app. From the app checkout and an activated
virtual environment:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The core itself supports Python 3.9+, but the Windows app requires 3.10+.
Developers do not need a sibling core checkout. `requirements.txt` contains
the pinned PEP 508 Git dependency for repeatable local installs.

## CI installation

All three CI jobs check out the core at the same verified commit. They install
app and core dependencies through `pip install -r requirements.txt`. The
Windows test job additionally runs core tests from its pinned checkout. The
build job uses the same dependency installation before invoking
`build_executable.py`.

## PyInstaller packaging

Build preflight checks that `face-mouse-pro-core==0.1.0` is installed and
importable. `FaceMousePro.spec` explicitly collects the installed package's
submodules with PyInstaller's `collect_submodules`; it does not require a
sibling source checkout. PyInstaller also analyzes the app's ordinary imports.

## Adapter responsibilities

- `src/core/gesture_detector.py` keeps the Windows constructor, optional clock
  fallback and state properties. `GestureAction` aliases the core's
  `GestureType`, so values are shared directly; there is no enum conversion
  layer. Settings dictionaries map to typed `GestureConfig`.
- `src/core/calibration.py` keeps neutral calibration state, logging, tuple
  arguments and return values. It delegates sample averaging and relative
  offset/deadzone calculations. JSON persistence remains in the app.
- `src/utils/helpers.py` preserves tuple-oriented imports as wrappers around
  shared EAR/MAR, EMA and One Euro algorithms.
- `src/core/mouse_controller.py` delegates signed power, sensitivity and
  inversion to `CursorMapper`, then applies screen pixel scaling, the existing
  four-pixel clamp and PyAutoGUI dispatch in the Windows app.
- Camera, HUD, keyboard flow, settings storage and gesture-to-mouse dispatch
  remain app-owned.

## Configuration and behavior notes

The constructor's default maximum blink frame count is 14; checked-in JSON sets
it to 12 and that configured value passes through unchanged. The bilateral
EAR-difference setting remains inert because runtime behavior suppresses any
frame where both eyes are below threshold. The controller's One Euro
parameters remain `min_cutoff=1.2`, `beta=0.04`, and `d_cutoff=1.0`. JSON
`smoothing_factor=0.65` is not reinterpreted.

The core ignores malformed landmark groups without changing gesture state and
requires monotonic gesture timestamps. Cursor One Euro filtering preserves
Windows behavior for non-increasing timestamps by passing the current value
through.

## Tests and remaining validation

Run the app suite with:

```powershell
python -m pytest tests -v
```

CI also runs `pytest face-mouse-pro-core/tests/ -v` from the SHA-pinned core
checkout. Before treating the integration as release-ready, run the full suite
and PyInstaller build on supported Windows/Python 3.10+, then launch the
packaged executable and verify camera access, gestures, cursor movement,
settings updates and shutdown on Windows hardware.
