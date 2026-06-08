import cv2
import threading
import time
import logging

# Configure local logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SharedCamera")

class SharedCamera:
    def __init__(self, src=0):
        self.src = src
        self.cap = None
        self.ref_count = 0
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.frame = None
        self.ret = False
        self.frame_id = 0
        self.thread = None
        self.running = False
        self.device_name = "Unknown Camera"
        self.width = 0
        self.height = 0

    def isOpened(self):
        with self.lock:
            return self.running

    def start(self):
        with self.lock:
            self.ref_count += 1
            logger.info(f"SharedCamera start requested. Ref count: {self.ref_count}")
            if not self.running:
                logger.info(f"Opening VideoCapture device with source index: {self.src}...")
                # Prioritize DirectShow (CAP_DSHOW) on Windows for virtual/webcam capture compatibility
                self.cap = cv2.VideoCapture(self.src, cv2.CAP_DSHOW)
                if not self.cap.isOpened():
                    logger.info("DirectShow failed to open, falling back to default camera API...")
                    self.cap = cv2.VideoCapture(self.src)
                
                if not self.cap.isOpened():
                    logger.error("Failed to open VideoCapture device")
                    self.ref_count -= 1
                    return False

                # Query and cache resolution
                self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                if self.src == 0:
                    self.device_name = "Built-in Laptop Webcam"
                elif self.src == 1:
                    self.device_name = "Reincubate Camo Virtual Camera"
                else:
                    self.device_name = f"Camera (Index {self.src})"

                logger.info("==========================================")
                logger.info(f"CAMERA SELECTED: Index {self.src}")
                logger.info(f"FRIENDLY NAME  : {self.device_name}")
                logger.info(f"RESOLUTION     : {self.width}x{self.height}")
                logger.info("==========================================")

                self.running = True
                self.thread = threading.Thread(target=self._update, name="SharedCameraThread", daemon=True)
                self.thread.start()
            return True

    def _update(self):
        logger.info("SharedCamera update thread started.")
        while self.running:
            if self.cap:
                ret, frame = self.cap.read()
                with self.lock:
                    self.ret = ret
                    if ret:
                        self.frame = frame
                        self.frame_id += 1
                        self.condition.notify_all()
                    else:
                        logger.warning("Failed to read frame from VideoCapture device")
            
            # If capture read failed or returned False, add a small sleep to avoid spinning
            if not self.ret:
                time.sleep(0.01)

        logger.info("SharedCamera update thread stopping.")

    def read(self, last_frame_id=-1, timeout=0.1):
        """
        Reads the latest frame. If last_frame_id is provided, it blocks until a
        new frame is captured (frame_id > last_frame_id) or the timeout expires.
        
        Returns: (ret, frame, frame_id)
        """
        with self.lock:
            if last_frame_id >= 0 and self.frame_id <= last_frame_id and self.running:
                # Wait for next frame event
                self.condition.wait(timeout=timeout)
            
            if self.frame is not None:
                return self.ret, self.frame.copy(), self.frame_id
            return False, None, self.frame_id

    def stop(self):
        with self.lock:
            if self.ref_count > 0:
                self.ref_count -= 1
            logger.info(f"SharedCamera stop requested. Ref count: {self.ref_count}")
            if self.ref_count == 0 and self.running:
                logger.info("Releasing VideoCapture device...")
                self.running = False
                # Notify any waiting threads so they can exit clean
                self.condition.notify_all()
                
                # Join thread safely
                if self.thread:
                    # Release lock temporarily so the thread can exit if it is blocked on lock
                    self.lock.release()
                    try:
                        self.thread.join(timeout=1.0)
                    finally:
                        self.lock.acquire()
                    self.thread = None
                
                if self.cap:
                    self.cap.release()
                    self.cap = None
                self.frame = None
                self.ret = False
                self.frame_id = 0

# Global Shared Camera Instance
import os

def detect_camera_index():
    if "CAMERA_INDEX" in os.environ:
        return int(os.environ["CAMERA_INDEX"])
    
    # Try index 1 first (phone webcam/Camo), fallback to index 0, checking for real non-black stream
    for idx in [1, 0]:
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            # Warm up and read a few frames to verify it isn't streaming solid black
            is_valid = False
            for _ in range(5):
                ret, frame = cap.read()
                if ret and frame is not None and frame.any():
                    is_valid = True
                    break
            cap.release()
            if is_valid:
                return idx
    return 0

camera_index = detect_camera_index()
logger.info(f"Initializing SharedCamera instance with source index: {camera_index}")
shared_camera = SharedCamera(camera_index)
