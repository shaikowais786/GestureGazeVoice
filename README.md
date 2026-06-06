# 👁️🎙️ GestureGazeVoice

GestureGazeVoice is a unified suite of next-generation accessibility and control tools. It brings together high-accuracy, offline local voice automation and contact-free hand gesture & eye-gaze mouse control. By providing an integrated central launcher, users can easily select and run either mode depending on their preference, while keeping both modules completely isolated, modular, and stable.

---

## 📂 Modules

### 1. Smart Voice Mode
An offline, local speech recognition system coupled with secure user voice biometrics.
* **Security & Authentication**: Utilizes speaker-recognition embeddings (via Resemblyzer) with cosine similarity validation to register, identify, and authenticate speaker profiles.
* **Offline Command Parsing**: Leverages the Vosk speech engine to recognize and process system commands locally without relying on external cloud APIs.
* **System Automation**: Native execution of system functions (such as volume control, screen brightness, window management, lock screen, and system shutdown) and application launching.
* **File Operations**: Full CRUD management of files and folders (e.g. creating documents, searching folders, moving files to the recycle bin) on the Desktop or OneDrive.

### 2. Smart Cursor Mode
A hands-free human-computer interaction system utilizing computer vision for cursor control and cheating detection.
* **Head & Eye Gaze Control**: Translates head pose pitch and eye direction movements into real-time screen cursor coordinates.
* **Blink Actions**: Smoothly captures eye blinks using eye aspect ratio (EAR) analysis to trigger precise single and double mouse clicks.
* **Gesture Actions**: Uses hand landmark tracking to detect index finger extension and motion for scroll gestures.
* **Real-time Diagnostic Page**: Fires up a local Flask server displaying live video feedback, face/hand bounding boxes, landmark tracking skeleton lines, and a diagnostics overlay.

---

## 📂 Folder Structure

```
GestureGazeVoice/
│
├── launcher.py                      # Main entry point (selector menu)
│
├── GestureGaze_Voice/               # Voice Automation Module
│   ├── actions/                     # Action dispatch and controllers
│   ├── models/                      # Vosk acoustic speech models
│   ├── modules/                     # Speech engines & speaker authentication
│   ├── security/                    # User session manager & voice database
│   ├── users/                       # Pickled voice templates database
│   ├── Voice Commands Manual.md      # Command cheatsheet and documentation
│   ├── README.md                    # Voice module specific README
│   ├── requirements.txt             # Voice module requirements
│   ├── main.py                      # Voice module entry point
│   ├── controller.py                # Voice state machine
│   ├── download_upgrade_model.py     # Script to download large model
│   └── revert_model.py              # Script to revert model to backup
│
├── Smart_Cursor/                    # Camera Gaze Control Module
│   ├── templates/                   # Flask web interface HTML templates
│   ├── static/                      # Flask static files (CSS, JS)
│   ├── app.py                       # Smart Cursor entry point & Flask server
│   ├── camera_manager.py            # Shared camera manager
│   ├── mouse_control.py             # Eye-gaze coordinates & gesture detection
│   ├── face_landmarker.task         # Mediapipe face model asset
│   ├── hand_landmarker.task         # Mediapipe hand model asset
│   └── yolov8n.pt                   # YOLO model file
│
└── README.md                        # Root documentation (this file)
```

---

## 💻 System Requirements

| Requirement | Details |
|-------------|---------|
| **Operating System** | Windows 10 or Windows 11 (required for Win32 API system commands and cursor integration) |
| **Python Version** | Python 3.8 – 3.11 supported. **Python 3.10 is highly recommended.** |
| **Microphone** | Any active recording device (built-in, USB, or Bluetooth). Required for Voice Mode. |
| **Webcam** | Any active camera device (built-in laptop webcam or external USB). Required for Smart Cursor Mode. |
| **Phone Camera (Optional)** | Reincubate Camo is supported as a virtual webcam source (connects an iPhone or Android phone camera to your PC). Set `camera_index = 1` in `Smart_Cursor/camera_manager.py` or use the `CAMERA_INDEX` environment variable. |
| **RAM** | Minimum 4 GB. 8 GB or more is recommended (both modules load ML models into memory). |

---

## 📦 Required Packages

All dependencies for both modules are consolidated in the root-level `requirements.txt`.

### Voice Module Dependencies
* `PyAudio` — Acoustic mic listener interface
* `Vosk` — Offline speech-to-text decoder
* `Resemblyzer` — Speaker voice embeddings extraction
* `pyttsx3` — Offline Text-to-Speech engine
* `pywin32` / `pypiwin32` — Windows COM and API control
* `SpeechRecognition` — Unified audio listening utilities
* `librosa`, `soundfile`, `sounddevice`, `scikit-learn` — Audio processing
* `python-docx`, `python-pptx`, `openpyxl` — Office file CRUD
* `PyAutoGUI`, `screen_brightness_control` — Automation controls
* `Send2Trash` — Safe file deletion (Recycle Bin)
* `torch` — PyTorch (used by Resemblyzer for speaker model inference)

### Smart Cursor Module Dependencies
* `opencv-python` — Image processing and camera capture
* `Flask` — Live diagnostic web dashboard
* `mediapipe` — Face and hand landmark tracking
* `ultralytics` — YOLOv8 mobile-phone and object detection
* `numpy` — Coordinate interpolation and math
* `pyautogui` — Cursor movement simulation

---

## 🆕 First-Time Setup (New Computer)

Follow these steps in order on a fresh Windows machine:

1. **Install Python 3.10**
   Download from [python.org](https://www.python.org/downloads/). During installation, check **"Add Python to PATH"**.

2. **Clone the Repository**
   ```bash
   git clone <your-repository-url>
   cd GestureGazeVoice
   ```

3. **Create and Activate a Virtual Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

4. **Install All Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   > **Note — PyAudio on Windows**: If `pip install PyAudio` fails with a compiler error, install it via a pre-compiled binary:
   > ```bash
   > pip install pipwin
   > pipwin install pyaudio
   > ```

5. **Download Voice Models**
   * Download the Vosk model `vosk-model-small-en-us-0.15` from [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models).
   * Extract it to `GestureGaze_Voice/models/model/`.
   * Alternatively, run the upgrade script for the high-accuracy model:
     ```bash
     cd GestureGaze_Voice
     python download_upgrade_model.py
     cd ..
     ```

6. **Download Cursor Models**
   * Ensure `face_landmarker.task` and `hand_landmarker.task` are placed directly inside the `Smart_Cursor/` directory.
   * Download from the [MediaPipe Solutions Guide](https://developers.google.com/mediapipe/solutions/vision/face_landmarker#models).

7. **Connect Hardware**
   * Plug in your microphone (for Voice Mode).
   * Plug in or enable your webcam (for Smart Cursor Mode).
   * If using Camo, install [Reincubate Camo](https://reincubate.com/camo/) on both your phone and PC.

8. **Verify Setup**
   ```bash
   python launcher.py
   ```
   Select Option 3 (Exit) to confirm the launcher runs without errors.

---

## 🚀 How to Run

### Option A — Using the Launcher (Recommended)
Run the central controller script from the root folder:
```bash
python launcher.py
```
This displays a menu selector interface:
```
========================================
      GestureGazeVoice Launcher
========================================
1. Smart Voice Mode
2. Smart Cursor Mode
3. Exit
========================================
Select an option (1-3):
```
Enter `1` or `2` to run the respective module, or `3` to exit. Pressing `Ctrl+C` inside an active module cleanly stops its loop and returns control to the launcher.

### Option B — Running Voice Module Directly
```bash
cd GestureGaze_Voice
python main.py
```
The system will initialize the microphone, calibrate for ambient noise, load voice profiles, and begin listening for the wake word (`voice mode activate`).

### Option C — Running Smart Cursor Directly
```bash
cd Smart_Cursor
python app.py
```
The Flask development server will start on `http://127.0.0.1:5000`. Open this URL in your browser to access the live diagnostic dashboard with video feed, face/hand tracking overlays, and mouse control toggles.

---

## 📖 Documentation

Both modules include detailed command reference manuals:

* **Voice Commands Manual** — Located at `GestureGaze_Voice/Voice Commands Manual.md`. Contains the full list of supported voice commands, wake word instructions, user registration flow, and system state descriptions.
* **EyeGesture Commands Manual** — Located at `Smart_Cursor/EyeGesture Commands Manual.md`. Contains Smart Cursor operational guidance including head-tracking calibration, blink-click usage, hand-gesture scrolling, and Exam Mode proctoring behavior.

---

## 🔧 Troubleshooting

* **PyAudio fails to compile**: Install Visual Studio C++ Build Tools or use `pipwin` / download a precompiled wheel (`.whl`) matching your Python version.
* **Microphone not detected**: Run `python list_mic_devices.py` or `python find_active_mic.py` inside `GestureGaze_Voice/` to identify and debug connected recording hardware.
* **Camera fails to start in Smart Cursor**: Make sure no other program is currently accessing the webcam. You can adjust the camera source index inside `Smart_Cursor/camera_manager.py` or set the `CAMERA_INDEX` environment variable.
* **Subprocess execution issues**: Make sure `python` is added to your environment `PATH` variables. The launcher runs scripts using the active python executable (`sys.executable`).
* **Voice Module shows `webrtcvad` warning**: This is a harmless deprecation notice from the `webrtcvad` package regarding `pkg_resources`. It does not affect functionality.
* **Flask server port conflict**: If port `5000` is already in use, either stop the conflicting process or modify the port in `Smart_Cursor/app.py`.
* **Torch installation is too large**: If you need a lightweight install, use `pip install torch --index-url https://download.pytorch.org/whl/cpu` for the CPU-only version.

---

## 🐙 GitHub Setup Instructions

A `.gitignore` file is included in the root directory. It excludes virtual environments, caches, model files, databases, and logs from version control.

1. **Initialize and Push**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit — GestureGazeVoice unified launcher"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Large Files**: Model files (`.pt`, `.task`) are excluded by `.gitignore`. If you want to include them, consider using [Git LFS](https://git-lfs.com/) to avoid repository size limits.

