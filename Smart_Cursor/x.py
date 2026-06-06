import cv2
import time
import math
import datetime
import mediapipe as mp
from ultralytics import YOLO
import base64

# =============================
# GLOBAL CONTROL
# =============================
terminated = False
snapshot_memory = []

# =============================
# LOAD MODELS
# =============================
yolo_model = YOLO("yolov8n.pt")
MOBILE_CLASS_ID = 67

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

MODEL_PATH = "face_landmarker.task"

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.VIDEO,
    num_faces=2
)

face_landmarker = FaceLandmarker.create_from_options(options)

# =============================
# SETTINGS
# =============================
PITCH_THRESHOLD = 50
FACE_MISSING_TIME = 2.0
CHEATING_LIMIT = 3
CHEAT_COOLDOWN = 1.0

last_cheat_time = 0
face_missing_start = None
cheating_count = 0
timestamp_ms = 0


# =============================
# SAVE IN MEMORY (NOT FILE)
# =============================
def save_screenshot(frame, reason):
    global snapshot_memory

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    _, buffer = cv2.imencode('.jpg', frame)
    encoded = base64.b64encode(buffer).decode('utf-8')

    snapshot_memory.append({
        "image": encoded,
        "reason": reason,
        "time": timestamp
    })


# =============================
# MAIN DETECTION LOOP
# =============================
def detection_loop(camera, save_folder=None):
    global terminated
    global cheating_count
    global last_cheat_time
    global face_missing_start
    global timestamp_ms

    while not terminated:

        ret, frame = camera.read()
        if not ret:
            continue

        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        cheating_detected = False
        reason = ""

        # -----------------------------
        # YOLO MOBILE DETECTION
        # -----------------------------
        results = yolo_model(frame)

        for r in results:
            for box in r.boxes:
                if int(box.cls[0]) == MOBILE_CLASS_ID:
                    cheating_detected = True
                    reason = "mobile_detected"

        # -----------------------------
        # FACE LANDMARK DETECTION
        # -----------------------------
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        result = face_landmarker.detect_for_video(mp_image, timestamp_ms)
        timestamp_ms += 33

        if len(result.face_landmarks) == 0:
            if face_missing_start is None:
                face_missing_start = time.time()
            elif time.time() - face_missing_start > FACE_MISSING_TIME:
                cheating_detected = True
                reason = "face_not_visible"
        else:
            face_missing_start = None

            if len(result.face_landmarks) > 1:
                cheating_detected = True
                reason = "multiple_persons"

        # -----------------------------
        # CHEATING HANDLER
        # -----------------------------
        now = time.time()

        if cheating_detected:
            if now - last_cheat_time >= CHEAT_COOLDOWN:
                cheating_count += 1
                last_cheat_time = now

                save_screenshot(frame, reason)
                print("Cheating:", cheating_count, reason)

        # -----------------------------
        # TERMINATION
        # -----------------------------
        if cheating_count >= CHEATING_LIMIT:
            save_screenshot(frame, "exam_terminated")
            terminated = True
            print("🚨 EXAM TERMINATED 🚨")
            break