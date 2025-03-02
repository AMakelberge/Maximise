import io
from flask import Flask, render_template, request, jsonify
import base64
from io import BytesIO
from PIL import Image
import server
import json

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/save", methods=["POST"])
async def save_image():
    try:
        data = request.get_json()
        image_data = data["image"].split(",")[1]  # Extract base64 data

        image = Image.open(BytesIO(base64.b64decode(image_data)))
        # Convert to RGB (JPEG does not support transparency)
        image = image.convert("RGBA")
        # Create a new white background
        background = Image.new("RGBA", image.size, (255, 255, 255, 255))  # White background
        # Paste the drawing on the white background
        image = Image.alpha_composite(background, image).convert("RGB")
        
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        image_bytes = buffer.getvalue()
        base64_str = base64.b64encode(image_bytes).decode('utf-8')

        rep = await server.process_message(base64_str)
        rep = json.loads(rep)
        print(rep["reply"])

        return jsonify({"success": True, "maximaCode": rep})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8765, debug=True)