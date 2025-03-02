from browser import document, websocket, window
import json

# Get references to HTML elements
canvas = document["canvas"]
ctx = canvas.getContext("2d")
maxima_div = document["maximaCode"]
submit_btn = document["submitBtn"]

# Variables to track drawing state
drawing = False

def mousedown(ev):
    global drawing
    drawing = True
    ctx.beginPath()
    ctx.moveTo(ev.offsetX, ev.offsetY)

def mousemove(ev):
    if drawing:
        ctx.lineTo(ev.offsetX, ev.offsetY)
        ctx.stroke()

def mouseup(ev):
    global drawing
    drawing = False

# Bind mouse events for drawing
canvas.bind("mousedown", mousedown)
canvas.bind("mousemove", mousemove)
canvas.bind("mouseup", mouseup)
canvas.bind("mouseout", mouseup)

# Set up WebSocket connection
ws_url = "ws://YOUR_SERVER_IP:8765"  # Replace YOUR_SERVER_IP with your server's IP address.
ws = websocket.WebSocket(ws_url)

def ws_open(ev):
    print("WebSocket connection established.")

def ws_message(ev):
    try:
        data = json.loads(ev.data)
        if data.get("status") == "success":
            maxima_div.textContent = data.get("reply")
        else:
            maxima_div.textContent = "Error: " + data.get("message")
    except Exception as e:
        print("Error parsing message:", e)

def ws_error(ev):
    print("WebSocket error:", ev)

ws.bind("open", ws_open)
ws.bind("message", ws_message)
ws.bind("error", ws_error)

def submit_click(ev):
    # Convert the canvas to a JPEG data URL
    data_url = canvas.toDataURL("image/jpeg", 0.9)
    # Remove the data URL prefix to keep only the base64 string
    base64_string = data_url.replace("data:image/jpeg;base64,", "")
    
    payload = json.dumps({
        "action": "upload_image",
        "data": base64_string
    })
    
    ws.send(payload)
    print("Payload sent.")

submit_btn.bind("click", submit_click)