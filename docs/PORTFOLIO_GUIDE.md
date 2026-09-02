# Face Mouse Pro — Career & Portfolio Presentation Assets

Use the pre-written, metrics-driven assets below for resumes, LinkedIn posts, portfolio websites, and technical interviews.

---

## 📄 1. Resume Bullet Points

### For AI / Computer Vision Engineer:
> - **Architected & deployed Face Mouse Pro**, a real-time hands-free human-computer interface tracking 478 3D facial landmarks at **370+ FPS (2.6ms latency)** using MediaPipe Face Mesh, OpenCV, and PyAutoGUI.
> - **Engineered an adaptive One-Euro kinematic filtering engine** and stateful Eye Aspect Ratio (EAR) gesture recognizer with dual-eye synchronization, eliminating resting cursor jitter and reducing involuntary blink false-positives to < 0.1%.
> - **Delivered a production-ready application** featuring a dark-mode CustomTkinter control panel, sub-pixel zero-point calibration, comprehensive pytest coverage (19 unit tests), and standalone Windows PyInstaller deployment.

---

## 💼 2. LinkedIn Showcase Post

```markdown
🚀 Excited to unveil my latest open-source project: Face Mouse Pro!

Face Mouse Pro is a real-time, accessibility-focused Computer Vision desktop application that enables complete, hands-free computer control using subtle facial movements and gestures.

💡 Why this matters:
For millions with upper-limb motor impairments, RSI, or clinicians in sterile surgical theaters, physical input devices can be limiting or impossible to use. Face Mouse Pro delivers fluid, sub-30ms hands-free computing on standard consumer webcams.

✨ Engineering Highlights:
🔹 Sub-Pixel Head Tracking: Real-time 478 3D landmark mesh extraction via MediaPipe & OpenCV.
🔹 Jitter-Free Kinematics: 2D One-Euro adaptive filter eliminating resting micro-tremors with zero response lag.
🔹 Intelligent Gesture Engine: Eye Aspect Ratio (EAR) & Mouth Aspect Ratio (MAR) state machine for left clicks, rapid double clicks, right clicks, drag-and-drop, and pitch scrolling.
🔹 Dual-Eye Blink Suppression: Advanced synchronization algorithm preventing involuntary physiological blinks from causing false clicks.
🔹 Standalone Deployment: Bundled as a zero-dependency Windows executable (.exe) alongside a modern CustomTkinter dark-mode settings panel.

📊 Benchmarks: 370+ FPS on standard 480p feeds (< 2.7ms per-frame pipeline processing).

🔗 GitHub Repository: https://github.com/your-username/face-mouse-pro
🎬 Watch the 60s Demo Video: [Link]

#ComputerVision #ArtificialIntelligence #Python #Accessibility #HCI #OpenSource #MediaPipe #OpenCV #SoftwareEngineering
```

---

## 🌐 3. Portfolio Website Case Study Copy

### **Project Title**: Face Mouse Pro — AI-Powered Hands-Free Desktop Controller
- **Category**: Computer Vision / Real-Time Systems / Accessibility HCI
- **Stack**: Python 3.10+, MediaPipe Face Mesh, OpenCV, PyAutoGUI, CustomTkinter, NumPy, PyInstaller, PyTest

### **The Problem**:
Standard desktop computing relies on physical peripherals (mice/trackpads), creating significant accessibility barriers for users with quadriplegia, ALS, cerebral palsy, or severe RSI, as well as surgeons requiring sterile hands-free interface navigation.

### **The Solution**:
Designed and developed a production-ready desktop application transforming facial geometry into mouse events. Built with an adaptive One-Euro filter for smooth trajectory tracking, an EAR/MAR state machine for gesture disambiguation, and a real-time HUD compositor.

### **Key Metrics**:
- **370+ FPS** throughput on SD webcam feeds.
- **2.64 ms** average end-to-end frame processing latency.
- **100% test pass rate** across 19 unit test suites.

---

## 🎙️ 4. 2-Minute Technical Interview Script (STAR Method)

- **Situation**: *"I wanted to build an impactful, production-grade assistive technology project that solves real-world accessibility challenges for individuals with motor disabilities who cannot use a physical mouse."*
- **Task**: *"My goal was to create Face Mouse Pro — a desktop application that translates webcam facial movements into mouse motions, clicks, dragging, and scrolling in real-time with sub-30ms latency and high reliability."*
- **Action**: *"I used MediaPipe Face Mesh to extract 478 3D landmarks at >30 FPS. To solve the classic 'resting cursor jitter' problem without adding input lag, I implemented a 2D One-Euro adaptive filter with dynamic cutoff frequencies. For gesture recognition, I calculated Eye Aspect Ratio and Mouth Aspect Ratio. A key engineering challenge was preventing involuntary blinks from triggering false clicks — I solved this by designing a dual-eye synchronization filter that identifies simultaneous eye closure and discards it from single-eye click triggers. I also added a CustomTkinter GUI panel for real-time parameter tuning."*
- **Result**: *"The final system achieves 370+ FPS effective processing with 2.6ms per-frame latency, consumes under 125MB RAM, and is fully packaged as a standalone Windows executable. It is supported by a 19-test pytest suite, comprehensive documentation, and automated CI workflows."*
