import re
import os

log_path = r"c:\project1\EyeGesture_Module\pipeline_debug.log"

if not os.path.exists(log_path):
    print(f"Error: {log_path} does not exist.")
    exit(1)

with open(log_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Lists for parsing
frames = []

for line in lines:
    if not line.startswith("Frame:"):
        continue
    
    parts = line.strip().split(" | ")
    part_dict = {}
    for p in parts:
        if ":" in p:
            k, v = p.split(":", 1)
            part_dict[k.strip()] = v.strip()
    frames.append(part_dict)

total_frames = len(frames)
face_detected_frames = 0
ear_all = []
ear_face_detected = []
ear_crossed_threshold_count = 0
blink_states_entered = 0
click_events = 0
double_click_events = 0

hand_detected_frames = 0
finger_y_detected_frames = 0
finger_y_values = []
scroll_events_generated = 0

# Track thresholds and state transitions
prev_below_thresh = None
prev_blink_state = None
prev_action = None

blink_durations = []
blink_exit_frames = []

for idx, f in enumerate(frames):
    frame_id = int(f.get("Frame", 0))
    face = f.get("Face") == "True"
    
    # 1. Face detected
    if face:
        face_detected_frames += 1
        
    # 2. EAR
    ear_str = f.get("EAR", "N/A")
    ear_val = None
    thresh_val = None
    if "N/A" not in ear_str:
        m = re.match(r"([\d\.]+)\s*\(Thresh:\s*([\d\.]+)\)", ear_str)
        if m:
            ear_val = float(m.group(1))
            thresh_val = float(m.group(2))
            ear_all.append(ear_val)
            if face:
                ear_face_detected.append(ear_val)
                
    # 3. EAR crossing threshold
    if ear_val is not None and thresh_val is not None:
        below_thresh = ear_val < thresh_val
        if prev_below_thresh is not None and below_thresh != prev_below_thresh:
            ear_crossed_threshold_count += 1
        prev_below_thresh = below_thresh
        
    # 4. Blink State transition
    blink_state = f.get("Blink State")
    if prev_blink_state is not None:
        if prev_blink_state != "Blinking" and blink_state == "Blinking":
            blink_states_entered += 1
    prev_blink_state = blink_state
    
    # 5. Clicks generated
    blink_dur_str = f.get("Blink Dur", "0.000s")
    blink_dur = float(blink_dur_str.replace("s", ""))
    
    if blink_state == "Open" and blink_dur > 0.0:
        blink_durations.append((frame_id, blink_dur))
        blink_exit_frames.append(f)
        if blink_dur > 0.6:
            double_click_events += 1
        elif blink_dur > 0.05: # BLINK_MIN is 0.05
            click_events += 1

    # 6. Hand Tracking
    hand = f.get("Hand") == "True"
    if hand:
        hand_detected_frames += 1
        
    finger_y_str = f.get("Finger Y", "N/A")
    finger_y = None
    if "N/A" not in finger_y_str:
        finger_y = float(finger_y_str)
        finger_y_values.append(finger_y)
        finger_y_detected_frames += 1

    # Action tracing
    action = f.get("Action")
    if prev_action is not None:
        if action != prev_action:
            if action in ["Scroll Up", "Scroll Down"]:
                scroll_events_generated += 1
    elif action in ["Scroll Up", "Scroll Down"]:
        scroll_events_generated += 1
    prev_action = action

print("=== Blink Detection Stats ===")
print(f"Number of frames processed: {total_frames}")
print(f"Number of frames with face detected: {face_detected_frames}")
if ear_face_detected:
    print(f"Minimum EAR observed (face detected): {min(ear_face_detected):.4f}")
    print(f"Maximum EAR observed (face detected): {max(ear_face_detected):.4f}")
    print(f"Average EAR observed (face detected): {sum(ear_face_detected)/len(ear_face_detected):.4f}")
else:
    print("Minimum/Maximum/Average EAR: N/A")
print(f"Number of times EAR crossed threshold: {ear_crossed_threshold_count}")
print(f"Number of blink states entered: {blink_states_entered}")
print(f"Number of click events generated: {click_events}")
print(f"Number of double click events generated: {double_click_events}")
print()
print("=== Hand Tracking Stats ===")
print(f"Number of frames with hand detected: {hand_detected_frames}")
print(f"Number of frames with index finger detected: {finger_y_detected_frames}")
if finger_y_values:
    print(f"Range of finger Y values: {min(finger_y_values):.4f} to {max(finger_y_values):.4f} (Span: {max(finger_y_values) - min(finger_y_values):.4f})")
else:
    print("Range of finger Y values: N/A")

scroll_frames = []
for idx, f in enumerate(frames):
    action = f.get("Action")
    if action in ["Scroll Up", "Scroll Down"]:
        scroll_frames.append((int(f.get("Frame")), action))

print(f"\nTotal Scroll Frames in Log: {len(scroll_frames)}")
if scroll_frames:
    print("Scroll segments:")
    current_action = None
    start_frame = None
    last_frame = None
    segments = []
    for frame_id, action in scroll_frames:
        if action != current_action or (last_frame is not None and frame_id - last_frame > 5):
            if current_action is not None:
                segments.append((current_action, start_frame, last_frame))
            current_action = action
            start_frame = frame_id
        last_frame = frame_id
    if current_action is not None:
        segments.append((current_action, start_frame, last_frame))
        
    for seg in segments:
        print(f"  Gesture: {seg[0]} | Frame Range: {seg[1]} - {seg[2]} | Length: {seg[2] - seg[1] + 1} frames")
        
    # Count of scroll gestures recognized (each segment represents a scroll event start)
    print(f"Number of scroll gestures recognized: {len(segments)}")
    print(f"Number of scroll events generated: {scroll_events_generated}")
else:
    print("Number of scroll gestures recognized: 0")
    print("Number of scroll events generated: 0")

print("\n=== Blink Exit Events ===")
for frame_id, dur in blink_durations:
    status = "Filtered"
    if dur > 0.6:
        status = "Double Click Generated"
    elif dur > 0.05:
        status = "Single Click Generated"
    print(f"  Exit at Frame {frame_id} | Duration: {dur:.4f}s | Result: {status}")
