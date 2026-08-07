from typing import List, Dict

import cv2

from .face_engine import get_faces
from .recognizer import recognize
from .database import get_student


# ==========================================================
# SETTINGS
# ==========================================================

UNKNOWN_NAME = "Unknown"
UNKNOWN_BRANCH = "Unknown"

MIN_CONFIDENCE = 0.55


# ==========================================================
# LIVE RECOGNITION
# ==========================================================

def recognize_frame(image) -> List[Dict]:
    """
    Detects every face in the frame and
    returns recognition results.
    """
    results = []

    faces = get_faces(image)

    if len(faces) == 0:
        return results

    for face in faces:

        x1, y1, x2, y2 = map(int, face.bbox)

        student_index, confidence = recognize(face.embedding)

        # --------------------------------------
        # UNKNOWN PERSON
        # --------------------------------------
        if student_index is None or confidence < MIN_CONFIDENCE:
            results.append({
                "matched": False,
                "name": UNKNOWN_NAME,
                "roll": "",
                "course": "",
                "semester": "",
                "stream": UNKNOWN_BRANCH,
                "section": "",
                "confidence": round(float(confidence), 4),
                "box": [x1, y1, x2, y2]
            })
            continue

        # --------------------------------------
        # KNOWN STUDENT
        # --------------------------------------
        student = get_student(student_index)

        results.append({
            "matched": True,
            "name": student["name"],
            "roll": student["roll"],
            "course": student["course"],
            "semester": student["semester"],
            "stream": student["stream"],
            "section": student["section"],
            "photo": student["photo"],
            "confidence": round(float(confidence), 4),
            "box": [x1, y1, x2, y2]
        })

    return results


# ==========================================================
# DRAW RESULTS
# ==========================================================

GREEN = (0, 255, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)


def draw_results(frame, results):
    """
    Draw bounding boxes and labels on a video frame.
    Shows Name + Stream + Semester.
    """
    for result in results:
        x1, y1, x2, y2 = result["box"]

        if result["matched"]:
            color = GREEN
            label = result["name"]
            semester = result.get("semester", "")
            stream = result.get("stream", "")
            sub_label = f"{stream} | Sem {semester}" if semester else stream
        else:
            color = RED
            label = "Unknown"
            sub_label = ""

        # Bounding Box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Name
        cv2.putText(
            frame, label, (x1, max(y1 - 12, 20)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2, cv2.LINE_AA
        )

        # Stream + Semester
        if sub_label:
            cv2.putText(
                frame, sub_label, (x1, y1 + 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, WHITE, 2, cv2.LINE_AA
            )

        # Confidence
        conf = int(result["confidence"] * 100)
        cv2.putText(
            frame, f"{conf}%", (x1, y2 + 22),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2, cv2.LINE_AA
        )

    return frame


# ==========================================================
# PROCESS FRAME
# ==========================================================

def process_frame(frame):
    """
    Complete pipeline: Detect → Recognize → Draw
    """
    results = recognize_frame(frame)
    annotated = draw_results(frame.copy(), results)
    return annotated, results