from insightface.app import FaceAnalysis
import numpy as np

app = FaceAnalysis()

app.prepare(ctx_id=-1)

def get_faces(image):

    faces = app.get(image)

    return faces