from insightface.app import FaceAnalysis

# Smaller model (~4x less RAM than buffalo_l)
app = FaceAnalysis(name="buffalo_s")

# CPU mode
app.prepare(ctx_id=-1)

def get_faces(image):
    return app.get(image)