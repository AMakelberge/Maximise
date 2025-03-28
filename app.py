import io
import base64, re, os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from io import BytesIO
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv
import compiler
import logging
logging.basicConfig(level=logging.INFO)
logging.info("Starting app...")

load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, ping_timeout=600, ping_interval=300)

converter = compiler.MaximaToLatex()

@app.route("/")
def index():
    return render_template("index.html")

def process_message(data):
    try:
        prompt = (
            "You are an expert in computer algebra systems. "
            "I have provided a base64 encoded image containing a mathematical expression. "
            "Your task is to extract the mathematical expression and convert it into the syntax for the symbolic mathematics package Maxima. "
            "Make special care of subscripts which should be written using an underscore if you find a subscript. "
            "Return only the Maxima code with no additional text, explanations, or formatting."
            "Additionally return the LaTeX version of the Maxima code after the Maxima code, this should be separated by a colon with no additional text, explanations, or formatting."
            "All code should be directly translated from the drawn image, you should add no new maths terms in."
            "Return one single line only containing the raw maxima code, a colon, then the raw latex code."
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
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.0
        )
        reply = response.choices[0].message.content.strip()
        print(reply)
        reply = re.sub(r"^```(?:\w+)?\s*", "", reply).replace(r"\[", "").replace(r"\]", "")
        reply = re.sub(r"\s*```$", "", reply).replace("`","").replace(";", "")
        if reply.startswith("(expr:"):
            reply = reply.replace("(expr:","")[:-1]
        if reply.startswith("A:"):
            reply = reply.replace("A:","")

        print(reply)
        maxima, latex = reply.split(":")
        # Convert Maxima code to LaTeX
        #latex_result = converter.convert(reply)

        #if "undefined" in latex_result:
        #    return {"status": "success", "reply": reply, "latex": ""}

        return {"status": "success", "reply": maxima, "latex": "$$" + latex + "$$"}
    except Exception as e:
        print('bob')
        print(e)
        return {"status": "error", "message": str(e)}

@socketio.on('send_image')
def handle_send_image(data):
    try:
        image_data = data["image"].split(",")[1]  
        image = Image.open(BytesIO(base64.b64decode(image_data)))
        image = image.convert("RGBA")
        background = Image.new("RGBA", image.size, (255, 255, 255, 255))
        image = Image.alpha_composite(background, image).convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        image_bytes = buffer.getvalue()
        base64_str = base64.b64encode(image_bytes).decode('utf-8')
        
        result = process_message(base64_str)
        print('result processed')
        print(result)
        emit("maxima_code", result)
    except Exception as e:
        emit("maxima_code", {"status": "error", "message": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    socketio.run(app, host="0.0.0.0", port=port, debug=True)