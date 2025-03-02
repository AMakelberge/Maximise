import io
import json, base64, re, os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from io import BytesIO
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode="eventlet")  # Requires eventlet or gevent installed

@app.route("/")
def index():
    return render_template("index.html")

def process_message(data):
    try:
        # Build a prompt instructing ChatGPT to extract and convert the math to Maxima code.
        prompt = (
            "You are an expert in computer algebra systems. "
            "I have provided a base64 encoded image containing a mathematical expression. "
            "Your task is to extract the mathematical expression and convert it into the syntax for the symbolic mathematics package Maxima. "
            "Make special care of subscripts which should be written using an underscore if you find a subscript. "
            "Return only the Maxima code with no additional text, explanations, or formatting."
        )
        messages = [
            {"role": "system", "content": "You are a helpful assistant that outputs only code when requested."},
            {"role": "user", 
             "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{data}"
                        }
                    }
                ]}
        ]
        response = client.chat.completions.create(
            model="gpt-4o",  # Ensure you have access to this model
            messages=messages,
            temperature=0.0
        )
        reply = response.choices[0].message.content.strip()
        # Remove code block formatting and extra characters
        reply = re.sub(r"^```(?:\w+)?\s*", "", reply)
        reply = re.sub(r"\s*```$", "", reply).replace(" ", "").replace(";", "")
        return {"status": "success", "reply": reply}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@socketio.on('send_image')
def handle_send_image(data):
    try:
        # data["image"] is assumed to be a data URL (e.g. "data:image/png;base64,....")
        image_data = data["image"].split(",")[1]  # Remove the header part
        # Process the image as before
        image = Image.open(BytesIO(base64.b64decode(image_data)))
        image = image.convert("RGBA")
        background = Image.new("RGBA", image.size, (255, 255, 255, 255))
        image = Image.alpha_composite(background, image).convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        image_bytes = buffer.getvalue()
        base64_str = base64.b64encode(image_bytes).decode('utf-8')
        
        result = process_message(base64_str)
        # Emit the result back to the client
        emit("maxima_code", result)
    except Exception as e:
        emit("maxima_code", {"status": "error", "message": str(e)})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8765, debug=True)