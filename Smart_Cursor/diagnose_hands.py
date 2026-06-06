import cv2
import mediapipe as mp
import numpy as np
import time
import os
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

print("=== Running Hand Tracking Diagnostics ===")

camera_idx = int(os.environ.get("CAMERA_INDEX", 1))
print(f"Using Camera Index: {camera_idx}")

# Initialize MediaPipe Hand Landmarker
# We can test different confidence levels. The default is 0.5.
hand_base = python.BaseOptions(model_asset_path="hand_landmarker.task")
hand_options = vision.HandLandmarkerOptions(
    base_options=hand_base,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)
hand_detector = vision.HandLandmarker.create_from_options(hand_options)

cap = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("DirectShow failed to open, falling back to default capture API...")
    cap = cv2.VideoCapture(camera_idx)

if not cap.isOpened():
    print(f"ERROR: Camera index {camera_idx} is not accessible.")
    hand_detector.close()
    exit(1)

# Warm up camera
for _ in range(5):
    cap.read()

total_frames = 0
hand_detected_frames = 0

print("Diagnostics running. Press 'q' or ESC in the video window to stop and output stats.")
print("Please raise your hand and perform scroll gestures in front of the camera index.")

# We will record stats for 2000 frames or until user exits
max_frames = 2000

while total_frames < max_frames:
    ret, frame = cap.read()
    if not ret:
        time.sleep(0.01)
        continue
        
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    
    # Process with MediaPipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = hand_detector.detect(mp_image)
    
    hand_present = len(result.hand_landmarks) > 0
    if hand_present:
        hand_detected_frames += 1
        
        # Draw hand landmarks
        landmarks = result.hand_landmarks[0]
        # We manually draw landmarks because MediPipe Task outputs are simple normalized lists
        for lm in landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
            
        # Draw connections
        # Define connection lines based on hand landmark indices
        connections = [
            (0,1), (1,2), (2,3), (3,4),
            (0,5), (5,6), (6,7), (7,8),
            (5,9), (9,10), (10,11), (11,12),
            (9,13), (13,14), (14,15), (15,16),
            (13,17), (17,18), (18,19), (19,20),
            (0,17)
        ]
        for conn in connections:
            pt1 = landmarks[conn[0]]
            pt2 = landmarks[conn[1]]
            cv2.line(frame, (int(pt1.x * w), int(pt1.y * h)), (int(pt2.x * w), int(pt2.y * h)), (255, 0, 0), 2)
            
        cv2.putText(frame, "Hand Detected", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "No Hand", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
    total_frames += 1
    
    # Overlay progress info
    cv2.putText(frame, f"Frame: {total_frames}/{max_frames}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    rate = (hand_detected_frames / total_frames) * 100
    cv2.putText(frame, f"Detection Rate: {rate:.1f}%", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    cv2.imshow("Hand Stability Diagnostics", frame)
    key = cv2.waitKey(1)
    if key in [27, ord('q')]:
        break

cap.release()
hand_detector.close()
cv2.destroyAllWindows()

# Output stats
print("\n=== HAND TRACKING DIAGNOSTICS REPORT ===")
print(f"Total Frames Processed: {total_frames}")
print(f"Frames with Hand Detected: {hand_detected_frames}")
print(f"Hand Detection Rate: {hand_detected_frames / total_frames * 100:.2f}%")
print("========================================")
