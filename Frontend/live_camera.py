# # Frontend/live_camera.py
# from typing import List, Dict
# import sys
# from pathlib import Path
# import av
# import cv2
# import numpy as np
# from streamlit_webrtc import VideoProcessorBase

# ROOT = Path(__file__).resolve().parent.parent
# sys.path.insert(0, str(ROOT))

# from Backend.live_recognition import process_frame, draw_results


# class FaceRecognitionProcessor(VideoProcessorBase):
#     def __init__(self):
#         self.latest_results: List[Dict] = []
#         self.frame_count = 0
#         self.process_every = 6          # ← very smooth (was 4)
#         self.max_width = 480            # ← aggressive resize for speed

#     def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
#         img = frame.to_ndarray(format="bgr24")
#         self.frame_count += 1

#         # Heavy recognition only every N frames
#         if self.frame_count % self.process_every == 0:
#             h, w = img.shape[:2]

#             # Resize for fast inference
#             if w > self.max_width:
#                 scale = self.max_width / w
#                 img_small = cv2.resize(img, (self.max_width, int(h * scale)))
#             else:
#                 img_small = img
#                 scale = 1.0

#             annotated_small, results = process_frame(img_small)
#             self.latest_results = results

#             # Scale boxes back to original resolution
#             if scale != 1.0:
#                 inv = 1.0 / scale
#                 for r in results:
#                     x1, y1, x2, y2 = r["box"]
#                     r["box"] = [int(x1 * inv), int(y1 * inv), int(x2 * inv), int(y2 * inv)]

#             # Draw on full resolution frame
#             annotated = self._draw(img, results)
#             return av.VideoFrame.from_ndarray(annotated, format="bgr24")

#         # Re-use last results (smooth video)
#         if self.latest_results:
#             annotated = self._draw(img, self.latest_results)
#             return av.VideoFrame.from_ndarray(annotated, format="bgr24")

#         return frame

#     def _draw(self, frame, results):
#         """Custom drawer that shows Name + Stream + Semester"""
#         for r in results:
#             x1, y1, x2, y2 = r["box"]

#             if r["matched"]:
#                 color = (0, 255, 0)          # Green
#                 name = r.get("name", "Unknown")
#                 stream = r.get("stream", "")
#                 semester = r.get("semester", "")
#                 label = name
#                 sub = f"{stream}  |  Sem {semester}" if semester else stream
#             else:
#                 color = (0, 0, 255)          # Red
#                 label = "Unknown"
#                 sub = ""

#             # Bounding box
#             cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

#             # Name
#             cv2.putText(
#                 frame, label, (x1, y1 - 12),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2, cv2.LINE_AA
#             )

#             # Stream + Semester
#             if sub:
#                 cv2.putText(
#                     frame, sub, (x1, y1 + 22),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA
#                 )

#             # Confidence
#             conf = int(r["confidence"] * 100)
#             cv2.putText(
#                 frame, f"{conf}%", (x1, y2 + 22),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2, cv2.LINE_AA
#             )

#         return frame