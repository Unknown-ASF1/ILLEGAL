from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import cv2
import numpy as np

from Backend.face_engine import get_faces
from Backend.recognizer import recognize
from Backend.database import (
    get_student,
    search_student,
    search_students
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
    field: str
    value: str

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
            (x.bbox[2]-x.bbox[0]) *
            (x.bbox[3]-x.bbox[1])
        )

        embedding = face.embedding

        student_index, confidence = recognize(
            embedding
        )

        if student_index is None:

            return {
                "matched": False,
                "message": "Student Not Found"
            }

        student = get_student(
            student_index
        )

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
# SEARCH STUDENT
# ==========================================================

@app.post("/search")
def search(request: SearchRequest):

    try:

        field = request.field

        value = request.value

        # Roll Number should return exactly one student

        if field == "Roll No":

            student = search_student(
                field,
                value
            )

            if student is None:

                return {

                    "found": False,

                    "message": "Student Not Found"

                }

            return {

                "found": True,

                "student": student

            }

        # Other fields may have multiple students

        students = search_students(
            field,
            value
        )

        return {

            "found": len(students) > 0,

            "count": len(students),

            "students": students

        }

    except Exception as e:

        return {

            "found": False,

            "message": str(e)

        }