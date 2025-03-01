import asyncio
import websockets
import json
import base64
from PIL import Image
import io

def preprocess_image(image_path, max_size=(800, 500), quality=50):
    with Image.open(image_path) as img:
        img.thumbnail(max_size)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        small_image_data = buffer.getvalue()
    return base64.b64encode(small_image_data).decode("utf-8")

async def send_image(image_path):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # Preprocess the image and get a base64-encoded string
        encoded_image = preprocess_image(image_path)
        
        # Construct the JSON message with the required action and preprocessed image data
        message = json.dumps({
            "action": "upload_image",
            "data": encoded_image
        })
        
        # Send the message to the server and wait for a response
        await websocket.send(message)
        print("Image uploaded. Awaiting response...")
        response = await websocket.recv()
        response_data = json.loads(response)
        if response_data.get("status") == "success":
            print("Received Maxima code:")
            print(response_data.get("reply"))
        else:
            print("Error:", response_data.get("message"))

if __name__ == "__main__":
    # Replace with the path to your image file containing the mathematical expression
    image_path = "images/bigBoi.jpg"
    asyncio.run(send_image(image_path))