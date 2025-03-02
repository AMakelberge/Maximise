from flask import Flask, render_template, request, jsonify
import base64
from io import BytesIO
from PIL import Image, ImageOps
import os
from client.client import do_main_part

app = Flask(__name__)

# Create 'static/images' directory if not exists
SAVE_DIR = "static/images"
os.makedirs(SAVE_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")  # Ensure this file exists in templates/

@app.route("/save", methods=["POST"])
def save_image():
    try:
        data = request.get_json()
        image_data = data["image"].split(",")[1]  # Extract base64 data
        image = Image.open(BytesIO(base64.b64decode(image_data)))

        # Convert to RGB (JPEG does not support transparency)
        image = image.convert("RGBA")

        # Create a new white background
        background = Image.new("RGBA", image.size, (255, 255, 255, 255))  # White background

        # Paste the drawing on the white background
        image = Image.alpha_composite(background, image).convert("RGB")  # Convert back to RGB

        filename = "drawing.jpg"
        filepath = os.path.join(SAVE_DIR, filename)

        image.save(filepath, "JPEG", quality=90)  # Save with high quality

        do_main_part(filepath)

        return jsonify({"success": True, "filename": filename, "filepath": filepath})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "main":
    app.run(debug=True)