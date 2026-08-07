# Frontend/live_camera.py
from typing import List, Dict
import sys
from pathlib import Path
import av
from streamlit_webrtc import VideoProcessorBase

# Make Backend importable when running from Frontend/
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from Backend.live_recognition import process_frame, draw_results


class FaceRecognitionProcessor(VideoProcessorBase):
    def __init__(self):
        self.latest_results: List[Dict] = []
        self.frame_count = 0
        self.process_every = 2

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        self.frame_count += 1

        if self.frame_count % self.process_every == 0:
            annotated, results = process_frame(img)
            self.latest_results = results
            return av.VideoFrame.from_ndarray(annotated, format="bgr24")
        else:
            if self.latest_results:
                annotated = draw_results(img.copy(), self.latest_results)
                return av.VideoFrame.from_ndarray(annotated, format="bgr24")
            return frame