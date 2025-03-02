let canvas = document.getElementById("drawCanvas");
let ctx = canvas.getContext("2d");
let codeField = document.getElementById("maximaCode");
let clearButton = document.getElementById("clearButton");
let savedImage = document.getElementById("savedImage")

const socket = io();

// Debounce timer to control how often we send updates
let debounceTimer;
const DEBOUNCE_DELAY = 2000; // milliseconds

// Detect if the device is touch-based
let isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints;

// Event listeners for drawing
let drawing = false;

if (isTouchDevice) {
    canvas.addEventListener("touchstart", startDrawing);
    canvas.addEventListener("touchmove", draw);
    canvas.addEventListener("touchend", stopDrawing);
} else {
    canvas.addEventListener("mousedown", startDrawing);
    canvas.addEventListener("mousemove", draw);
    canvas.addEventListener("mouseup", stopDrawing);
}

function startDrawing(event) {
    drawing = true;
    ctx.beginPath();
    let pos = getPosition(event);
    ctx.moveTo(pos.x, pos.y);
    // Clear any pending debounce when starting a new stroke
    clearTimeout(debounceTimer);
}

function draw(event) {
    if (!drawing) return;
    let pos = getPosition(event);
    ctx.lineTo(pos.x, pos.y);
    ctx.strokeStyle = "black";
    ctx.lineWidth = 3;
    ctx.lineCap = "round";
    ctx.stroke();
}

function stopDrawing() {
    drawing = false;
    ctx.closePath();
    // Debounce sending the image data until after a pause in drawing
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(sendDrawing, DEBOUNCE_DELAY);
}

function getPosition(event) {
    let rect = canvas.getBoundingClientRect();
    let x = isTouchDevice ? event.touches[0].clientX - rect.left : event.clientX - rect.left;
    let y = isTouchDevice ? event.touches[0].clientY - rect.top : event.clientY - rect.top;
    return { x, y };
}

function sendDrawing() {
    let imageData = canvas.toDataURL("image/png");
    savedImage.src = imageData
    // Emit the image data to the server via websocket
    socket.emit("send_image", { image: imageData });
}

// Listen for the server's response and update the maximaCode field.
socket.on("maxima_code", function(data) {
    if (data.status === "success") {
        codeField.innerText = data.reply;
    } else {
        codeField.innerText = "Error: " + data.message;
    }
});

clearButton.addEventListener("click", clearCanvas);
function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Optionally clear the output field when clearing the canvas
    codeField.innerText = "Awaiting Input";
}