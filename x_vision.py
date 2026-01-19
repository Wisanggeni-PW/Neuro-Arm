import cv2
import threading
from ultralytics import YOLO
import time

class VisionStream:
    def __init__(self, model_path="yolov8m.pt", camera_index=0):
        self.model = YOLO(model_path)

        # Only detect your specified classes
        self.allowed_classes = [39, 41, 42, 44, 45]

        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.latest_detections = []  # updated every frame
        self.running = False

    def start(self):
        if self.running:
            return
        self.running = True
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        while self.running:
            success, frame = self.cap.read()
            if not success:
                continue

            # Run YOLO with class filter
            results = self.model(
                frame,
                classes=self.allowed_classes,
                stream=False,
                conf=0.6,
                verbose=False
            )

            detections = []
            result = results[0]

            if result.boxes is not None:
                for box in result.boxes:
                    cls = int(box.cls[0])

                    if cls not in self.allowed_classes:
                        continue

                    x1, y1, x2, y2 = map(float, box.xyxy[0].tolist())
                    label = self.model.names[cls]

                    detections.append({
                        "label": label,
                        "cls": cls,
                        "bbox": (x1, y1, x2, y2)
                    })

            self.latest_detections = detections

            display = result.plot()
            cv2.imshow("Camera", display)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.running = False

            time.sleep(0.01)

        self.cap.release()
        cv2.destroyAllWindows()

    def get_objects(self, label):
        """Return all detected objects that match the label"""
        return [d for d in self.latest_detections if d["label"] == label]

    def stop(self):
        self.running = False
