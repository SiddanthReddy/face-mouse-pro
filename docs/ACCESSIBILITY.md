# Face Mouse Pro — Comprehensive Accessibility & HCI Evaluation

## 1. Accessibility Mission
**Face Mouse Pro** is engineered to dismantle physical interaction barriers between individuals and digital computing environments. By converting facial topology and gaze kinematics into low-latency OS input commands, the application provides an autonomous computing experience for diverse mobility profiles.

---

## 2. Target User Profiles & Assistive Use Cases

### 2.1 Motor & Physical Mobility Impairments
- **Spinal Cord Injuries (Quadriplegia / Tetraplegia)**: Enables comprehensive desktop computing without requiring upper limb movement or specialized mouth-sticks.
- **Motor Neuron Disease (ALS)** & **Cerebral Palsy**: Provides customizable deadzones and sensitivity curves that compensate for muscle spasticity or reduced head motion range.
- **Muscular Dystrophy**: Minimizes physical exertion through adaptive acceleration.

### 2.2 Repetitive Strain Injury (RSI) & Rehabilitation
- **Carpal Tunnel Syndrome & Tendonitis**: Offers complete wrist and hand offloading during acute rehabilitation or extended writing sessions.
- **Ergonomic Break Alternation**: Allows software engineers and writers to alternate between physical peripherals and hands-free facial navigation.

### 2.3 Sterile & Hands-Free Industrial Environments
- **Operating Theaters & Medical Imaging**: Surgeons and radiologists can review CT/MRI DICOM scans hands-free without breaking surgical sterility.
- **Cleanrooms & Chemical Laboratories**: Laboratory technicians wearing hazardous material protection can navigate protocols and data sheets.

---

## 3. Ergonomic Design & Fatigue Mitigation

```
+-----------------------------------------------------------------------------------+
| Feature                    | Ergonomic Advantage                                  |
+-----------------------------------------------------------------------------------+
| Neutral Zero Calibration   | Calibrates to the user's natural resting posture     |
|                            | rather than forcing a rigid upright stance.          |
+-----------------------------------------------------------------------------------+
| Non-Linear Acceleration    | Small head tilts handle local clicking; accelerated   |
|                            | curves cross multi-monitor workspaces effortlessly.  |
+-----------------------------------------------------------------------------------+
| Involuntary Blink Filter   | Eliminates mental tension of trying not to blink     |
|                            | normally during work.                                |
+-----------------------------------------------------------------------------------+
| Motion Deadzones           | Absorbs micro-tremors and resting head drift.        |
+-----------------------------------------------------------------------------------+
```

---

## 4. WCAG 2.2 & Assistive Technology Alignment

- **Guideline 2.1 (Keyboard & Input Accessible)**: All functionality can be engaged without timed multi-finger dexterity.
- **Guideline 2.2 (Enough Time)**: Double-click window and long-blink duration are user-configurable from 200ms to 1500ms.
- **Guideline 2.5 (Input Modalities)**: Operates independently of standard mouse hardware.

---

## 5. Known Constraints & Practical Recommendations

1. **Illumination Requirements**: Reliable landmark tracking requires at least 150 lux frontal illumination. Backlit environments can degrade eye landmark precision.
2. **Facial Obstructions**: Thick-rimmed glasses or heavy bangs obscuring outer eye corners may require increasing the `blink_ear_threshold` to `0.23-0.25`.
