from flask import Flask, render_template, request, jsonify
import openai
import base64
import re
from dotenv import load_dotenv
from openai import OpenAI
import os

app = Flask(__name__)

# Set your OpenAI API key (ideally, load from environment variables)
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    try:
        data = request.get_json()
        if data.get("action") == "upload_image":
            encoded_image = data.get("data")
            # Decode the base64 image data into binary bytes
            image_bytes = base64.b64decode(encoded_image)
            
            # Build a prompt instructing GPT-4o to extract and convert the math expression into Maxima code.
            prompt = (
                "You are an expert in computer algebra systems. "
                "I have provided a base64 encoded image containing a mathematical expression. "
                "Your task is to extract the mathematical expression and convert it into the syntax for the symbolic mathematics package Maxima."
                "Make special care of subscripts which should be written using an underscore if you find a subscript."
                "Return only the Maxima code with no additional text, explanations, or formatting."
            )
            messages = [
                {"role": "system", "content": "You are a helpful assistant that outputs only code when requested."},
                {"role": "user", 
                 "content": [
                     {
                         "type": "text",
                         "text": f"{prompt}"
                     },
                     {
                         "type": "image_url",
                         "image_url": {
                             "url": f"data:image/jpeg;base64,{image_bytes}"
                         }
                     }
                 ]}
            ]
            response = client.chat.completions.create(model="gpt-4o",  # use a model you have access to
            messages=messages,
            temperature=0.0)
            reply = response.choices[0].message.content.strip()
            reply = re.sub(r"^```(?:\w+)?\s*", "", reply)
            reply = re.sub(r"\s*```$", "", reply).replace(" ","")
            return jsonify({"status": "success", "reply": reply})
        else:
            return jsonify({"status": "error", "message": "Unknown action"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    # Run the Flask app so it's available on your network
    app.run(host="0.0.0.0", port=8765, debug=True)