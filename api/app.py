from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from ImageBuilder import resizeImage, build
from utils import read, send

# Constants
RATE_LIMIT = 5
MEGABYTE = 2 ** 20
MAX_REQUEST_SIZE = 8
MAX_IMAGE_SIZE = 10000
MAX_BASE_TO_BLOCK_RATIO = 100
MAX_IMAGE_LIST_LENGTH = 250

# Flask app setup
app = Flask(__name__)
limiter = Limiter(
    app = app,
    key_func = get_remote_address,
    default_limits = [f"{RATE_LIMIT * 6 * 15} per day", f"{RATE_LIMIT * 15} per hour"],
    storage_uri = "memory://"
)
CORS(app)


# JPEG image conversion request
@app.route("/jpeg", methods = ["POST"])
@limiter.limit(f"{RATE_LIMIT} per minute")
def jpeg():
    # Exits if the request is too large
    if request.content_length / MEGABYTE > MAX_REQUEST_SIZE:
        return jsonify({ "error": f"Request content too large ({int(request.content_length / MEGABYTE)}MB vs {MAX_REQUEST_SIZE}MB)" })
    
    try:
        # Gets the quality and base image (decoded) from request
        quality = int(request.form["quality"])
        base = read(request.files["baseImage"].read())

        # Input validation and error responses
        if max(base.shape[1], base.shape[0]) > MAX_IMAGE_SIZE:
            return jsonify({ "error": f"Image dimensions are too large ({int(max(base.shape[1], base.shape[0]))} vs {MAX_IMAGE_SIZE})" })
        if quality < 0 or quality > 100:
            return jsonify({ "error": f"Invalid base image opacity ({quality} vs 0 - 100)" })
        
        # Converts the image and sends it
        return send(base, { "type": "jpeg", "quality": quality })
    
    except Exception:
        return jsonify({ "error": "Invalid file types or values" })

# Resize image request
@app.route("/resize", methods = ["POST"])
@limiter.limit(f"{RATE_LIMIT} per minute")
def resize():
    # Exits if the request is too large
    if request.content_length / MEGABYTE > MAX_REQUEST_SIZE:
        return jsonify({ "error": f"Request content too large ({int(request.content_length / MEGABYTE)}MB vs {MAX_REQUEST_SIZE}MB)" })

    try:
        # Gets the new width, height, and base image (decoded) from request
        width = int(request.form["imageWidth"])
        height = int(request.form["imageHeight"] or "0")
        base = read(request.files["baseImage"].read())

        # Input validation and error responses
        if max(base.shape[1], base.shape[0]) > MAX_IMAGE_SIZE:
            return jsonify({ "error": f"Image dimensions are too large ({int(max(base.shape[1], base.shape[0]))} vs {MAX_IMAGE_SIZE})" })
        if max(width, height) > MAX_IMAGE_SIZE:
            return jsonify({ "error": f"New image dimensions are too large ({int(max(width, height))} vs {MAX_IMAGE_SIZE})" })

        # Resizes the image and sends it
        return send(resizeImage(base, width, height), { "type": "png" })
    
    except Exception:
        return jsonify({ "error": "Invalid file types or values" })

# Compose image request
@app.route("/compose", methods = ["POST"])
@limiter.limit(f"{RATE_LIMIT} per minute")
def compose():
    # Exits if the request is too large
    if request.content_length / MEGABYTE > MAX_REQUEST_SIZE * 8:
        return jsonify({ "error": f"Request content too large ({int(request.content_length / MEGABYTE)}MB vs {MAX_REQUEST_SIZE * 8}MB)" })

    try:
        # Gets the images size, base presence, base image (decoded), and image list (decoded) from request
        size = int(request.form["imagesSize"])
        basePresence = float(request.form["basePresence"])
        base = read(request.files["baseImage"].read())
        imageList = [read(image.read()) for image in request.files.getlist("imageList")]

        # Input validation and error responses
        if max(base.shape[1], base.shape[0]) > MAX_IMAGE_SIZE:
            return jsonify({ "error": f"Base image dimensions are too large ({int(max(base.shape[1], base.shape[0]))} vs {MAX_IMAGE_SIZE})" })
        if size > max(base.shape[1], base.shape[0]):
            return jsonify({ "error": f"Block size is too large ({size} vs {max(base.shape[1], base.shape[0])})" })
        if (base.shape[1] * base.shape[0]) ** 0.5 / size > MAX_BASE_TO_BLOCK_RATIO:
            return jsonify({ "error": f"Base image to block size ratio is too large ({int((base.shape[1] * base.shape[0]) ** 0.5 / size)} vs {MAX_BASE_TO_BLOCK_RATIO})" })
        if len(imageList) > MAX_IMAGE_LIST_LENGTH:
            return jsonify({ "error": f"Too many block images ({len(imageList)} vs {MAX_IMAGE_LIST_LENGTH})" })
        if basePresence < 0 or basePresence > 1:
            return jsonify({ "error": f"Invalid base image opacity ({basePresence} vs 0 - 1)" })

        # Builds the image and sends it
        return send(build(base, imageList, size, basePresence), { "type": "png" })
    
    except Exception:
        return jsonify({ "error": "Invalid file types or values" })

if __name__ == "__main__":
    app.run(debug = True)