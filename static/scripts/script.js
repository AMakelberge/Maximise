let canvas = document.getElementById("drawCanvas");
let ctx = canvas.getContext("2d");
let codeField = document.getElementById("maximaCode");
let renderedField = document.getElementById("maximaRendered");
let clearButton = document.getElementById("clearButton");
let submitButton = document.getElementById("submitButton");

const socket = io();

let debounceTimer;
const DEBOUNCE_DELAY = 500;
let isProcessing = false;
let drawing = false;
let isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints;

canvas.width = 500;
canvas.height = 300;
ctx.fillStyle = "white";
ctx.fillRect(0,0,canvas.width, canvas.height)

// Prevent scrolling when touching the canvas.
canvas.addEventListener("touchstart", (event) => event.preventDefault(), { passive: false });
canvas.addEventListener("touchmove", (event) => event.preventDefault(), { passive: false });

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

function stopDrawing(event) {
    drawing = false;
    ctx.closePath();
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(sendDrawing, DEBOUNCE_DELAY);
}

// Define getPosition to extract the correct coordinates from the event.
function getPosition(event) {
    let rect = canvas.getBoundingClientRect();
    // For touch events, use the first touch's clientX/clientY.
    let x = isTouchDevice ? event.touches[0].clientX - rect.left : event.clientX - rect.left;
    let y = isTouchDevice ? event.touches[0].clientY - rect.top : event.clientY - rect.top;
    return { x, y };
}

//submitButton.addEventListener("click", sendDrawing)
function sendDrawing() {
    if (isProcessing) return;
    let imageData = canvas.toDataURL("image/png");
    isProcessing = true;
    socket.emit("send_image", { image: imageData });
}

socket.on("maxima_code", function(data) {
    isProcessing = false;
    console.log(data.reply)
    codeField.innerText = data.reply;
    renderedField.innerHTML = `${data.latex}`;
    MathJax.Hub.Queue(["Typeset", MathJax.Hub, document.getElementById("maximaRendered")]);
    MathJax.typeset();
});

clearButton.addEventListener("click", () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    codeField.innerText = "Awaiting Input.";
    renderedField.innerHTML = `Awaiting Input.`;
});
