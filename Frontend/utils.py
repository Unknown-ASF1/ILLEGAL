from PIL import Image


def load_image(uploaded_file):
    return Image.open(uploaded_file)