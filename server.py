import asyncio
import websockets
import json
from openai import OpenAI
import re
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import base64

# Set your ChatGPT API token

async def process_message(message):
    try:
        msg = json.loads(message)
        action = msg.get("action")
        data = msg.get("data")
        if action == "upload_image":
            # Build a prompt instructing ChatGPT to extract and convert the math to Maxima code.
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
                             "url": f"data:image/jpeg;base64,{data}"
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
            return json.dumps({"status": "success", "reply": reply})
        else:
            return json.dumps({"status": "error", "message": "Unknown action"})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

async def handler(websocket):
    async for message in websocket:
        print("Received message")
        response = await process_message(message)
        await websocket.send(response)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("Server started on ws://10.99.45.201:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())