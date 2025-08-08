from flask import send_file
from io import BytesIO
import cv2
import numpy as np

# Encodes an image as a PNG
def encode_PNG(image):
    success, img_data = cv2.imencode(".png", image)
    if not success:
        return None
    return img_data

# Encodes an image as a JPEG with given quality
def encode_JPG(image, quality):
    params = [cv2.IMWRITE_JPEG_QUALITY, quality]
    success, img_data = cv2.imencode(".jpg", image, params)
    if not success:
        return None
    return img_data

# Stores the given image in a BytesIO object, then returns a response object
def send(image, properties):
    if (properties["type"] == "png"):
        img_data = encode_PNG(image)
    elif (properties["type"] == "jpeg"):
        img_data = encode_JPG(image, properties["quality"])
    else:
        return None

    output = BytesIO()
    output.write(img_data)
    output.seek(0)
    return send_file(output, f"image/{properties['type']}")

# Decodes the given buffer and returns an image
def read(buffer):
    return cv2.imdecode(np.frombuffer(buffer, np.uint8), cv2.IMREAD_UNCHANGED)