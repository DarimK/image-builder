from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from ImageBuilder import resizeImage, build
from utils import readPNG, sendPNG


# Flask app setup
app = Flask(__name__)
limiter = Limiter(
    app = app,
    key_func = get_remote_address,
    default_limits = ["720 per day", "60 per hour"],
    storage_uri = "memory://"
)
CORS(app)

# Constants
MAX_IMAGE_SIZE = 1024
MAX_BASE_TO_BLOCK_RATIO = 256


# Resize image request
@app.route("/resize", methods = ["POST"])
@limiter.limit("5 per minute")
def resize():
    # Aborts if the request is too large
    if request.content_length > (MAX_IMAGE_SIZE * 2) ** 2:
        return jsonify({ "error": f"Request content too large ({request.content_length} vs {(MAX_IMAGE_SIZE * 2) ** 2})" })

    try:
        # Gets the new width, height, and base image (decoded) from request
        width = int(request.form["imageWidth"])
        height = int(request.form["imageHeight"])
        base = readPNG(request.files["baseImage"].read())

        # Resizes the image and sends it
        return sendPNG(resizeImage(base, width, height))
    
    except Exception as e:
        return jsonify({ "error": str(e) })

# Compose image request
@app.route("/compose", methods = ["POST"])
@limiter.limit("5 per minute")
def compose():
    # Aborts if the request is too large
    if request.content_length > 64 * MAX_IMAGE_SIZE ** 2:
        return jsonify({ "error": f"Request content too large ({request.content_length} vs {64 * MAX_IMAGE_SIZE ** 2})" })

    try:
        # Gets the images size, base presence, base image (decoded), and image list (decoded) from request
        size = int(request.form["imagesSize"])
        basePresence = float(request.form["basePresence"])
        base = readPNG(request.files["baseImage"].read())
        imageList = [readPNG(image.read()) for image in request.files.getlist("imageList")]

        # Exits if the base image to image block ratio is too large
        if (base.shape[1] * base.shape[0]) ** 0.5 / size > MAX_BASE_TO_BLOCK_RATIO:
            return jsonify({ "error": f"Base image size to block size ratio is too large ({int((base.shape[1] * base.shape[0]) ** 0.5 / size)} vs {MAX_BASE_TO_BLOCK_RATIO})" })

        # Builds the image and sends it
        return sendPNG(build(base, imageList, size, basePresence))
    
    except Exception as e:
        return jsonify({ "error": str(e) })