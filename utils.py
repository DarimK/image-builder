from flask import send_file
from io import BytesIO
import cv2
import numpy as np

# Encodes and stores the given image in a BytesIO object, then returns a response object
def sendPNG(image):
    _, img_data = cv2.imencode(".png", image)
    output = BytesIO()
    output.write(img_data)
    output.seek(0)
    return send_file(output, mimetype="image/png")

# Decodes the given buffer and returns an image
def readPNG(buffer):
    return cv2.imdecode(np.frombuffer(buffer, np.uint8), cv2.IMREAD_UNCHANGED)