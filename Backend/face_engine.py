from insightface.app import FaceAnalysis

app = FaceAnalysis(name="buffalo_s")

app.prepare(
    ctx_id=-1,
    det_size=(320,320)
)

def get_faces(image):
    return app.get(image)