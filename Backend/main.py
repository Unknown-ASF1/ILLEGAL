from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import cv2
import numpy as np

from Backend.face_engine import get_faces
from Backend.recognizer import recognize
from Backend.database import get_student

app = FastAPI(title="Student Recognition API")

# Allow Streamlit to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "status": "running",
        "message": "Student Recognition API"
    }


@app.post("/recognize")
async def recognize_student(file: UploadFile = File(...)):

    # Read uploaded image
    contents = await file.read()

    image = np.frombuffer(contents, np.uint8)

    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    if image is None:
        return {
            "matched": False,
            "message": "Invalid image."
        }

    # Detect faces
    faces = get_faces(image)

    faces = sorted(
    faces,
    key=lambda x: (x.bbox[2]-x.bbox[0])*(x.bbox[3]-x.bbox[1]),
    reverse=True
)

    if len(faces) == 0:
        return {
            "matched": False,
            "message": "No face detected."
        }

    # Use the largest detected face
    face = max(
        faces,
        key=lambda x: (x.bbox[2]-x.bbox[0])*(x.bbox[3]-x.bbox[1])
    )

    embedding = face.embedding

    student_index, confidence = recognize(embedding)

    if student_index is None:
        return {
            "matched": False
        }

    student = get_student(student_index)

    return {
        "matched": True,
        "confidence": round(confidence, 4),
        "student": student
    }