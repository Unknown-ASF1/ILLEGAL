from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import cv2
import numpy as np

from Backend.face_engine import get_faces
from Backend.recognizer import recognize
from Backend.database import (
    get_student,
    search_best_matches,
)

# ==========================================================
# APP
# ==========================================================

app = FastAPI(
    title="Student Recognition API"
)

# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# SEARCH MODEL
# ==========================================================

class SearchRequest(BaseModel):

    roll: str = ""
    name: str = ""
    course: str = ""
    semester: str = ""
    stream: str = ""
    section: str = ""

# ==========================================================
# HOME
# ==========================================================

@app.get("/")
def home():

    return {
        "status": "running",
        "message": "Student Recognition API"
    }

# ==========================================================
# FACE RECOGNITION
# ==========================================================

@app.post("/recognize")
async def recognize_student(
    file: UploadFile = File(...)
):

    try:

        contents = await file.read()

        image = np.frombuffer(
            contents,
            np.uint8
        )

        image = cv2.imdecode(
            image,
            cv2.IMREAD_COLOR
        )

        if image is None:

            return {
                "matched": False,
                "message": "Invalid Image"
            }

        faces = get_faces(image)

        if len(faces) == 0:

            return {
                "matched": False,
                "message": "No Face Found"
            }

        face = max(
            faces,
            key=lambda x:
            (x.bbox[2] - x.bbox[0]) *
            (x.bbox[3] - x.bbox[1])
        )

        student_index, confidence = recognize(
            face.embedding
        )

        if student_index is None:

            return {
                "matched": False,
                "message": "Student Not Found"
            }

        student = get_student(student_index)

        return {

            "matched": True,

            "confidence": round(
                confidence,
                4
            ),

            "student": student

        }

    except Exception as e:

        return {

            "matched": False,

            "message": str(e)

        }

# ==========================================================
# MULTI-FIELD SEARCH
# ==========================================================

@app.post("/search")
def search_students(request: SearchRequest):

    try:

        filters = {
            "roll": request.roll,
            "name": request.name,
            "course": request.course,
            "semester": request.semester,
            "stream": request.stream,
            "section": request.section,
        }

        # Check if every field is empty

        if not any(
            str(value).strip()
            for value in filters.values()
        ):

            return {
                "found": False,
                "count": 0,
                "message": "Please enter at least one search field.",
                "students": []
            }

        students = search_best_matches(filters)

        if len(students) == 0:

            return {
                "found": False,
                "count": 0,
                "message": "No matching students found.",
                "students": []
            }

        return {
            "found": True,
            "count": len(students),
            "students": students
        }

    except Exception as e:

        return {
            "found": False,
            "count": 0,
            "message": str(e),
            "students": []
        }


# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.get("/health")
def health():

    return {
        "status": "online",
        "service": "Student Recognition API"
    }