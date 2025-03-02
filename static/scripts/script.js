let canvas = document.getElementById("drawCanvas");
let ctx = canvas.getContext("2d");
let drawing = false;
let codeField = document.getElementById("maximaCode")
let confirmButton = document.getElementById("confirmButton")
let clearButton = document.getElementById("clearButton")

// Detect if the device is touch-based (iPad, iPhone, etc.)
let isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints;

// Event listeners for drawing
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
}

function draw(event) {
    if (!drawing) return;
    let pos = getPosition(event);
    ctx.lineTo(pos.x, pos.y);
    ctx.strokeStyle = "black";  // Drawing color
    ctx.lineWidth = 3;
    ctx.lineCap = "round";
    ctx.stroke();
}

function stopDrawing() {
    drawing = false;
    ctx.closePath();
    //saveDrawing()
}

function getPosition(event) {
    let rect = canvas.getBoundingClientRect();
    let x = isTouchDevice ? event.touches[0].clientX - rect.left : event.clientX - rect.left;
    let y = isTouchDevice ? event.touches[0].clientY - rect.top : event.clientY - rect.top;
    return { x, y };
}

clearButton.addEventListener("click", clearCanvas)
function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

confirmButton.addEventListener("click", saveDrawing)
function saveDrawing() {
    let imageData = canvas.toDataURL("image/png"); // Convert drawing to JPEG
    fetch("/save", {
        method: "POST",
        body: JSON.stringify({ image: imageData }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
         document.getElementById("savedImage").src = imageData;
         document.getElementById("maximaCode").innerText = data.maximaCode.reply;
    })
    .catch(error => console.error("Error saving image:", error));
}

async function preprocessImage(imagePath, maxSize = { width: 800, height: 500 }, quality = 50) {
    try {
      const buffer = await sharp(imagePath)
        .resize(maxSize.width, maxSize.height, { fit: 'inside' })
        .jpeg({ quality: quality })
        .toBuffer();
      return buffer;
    } catch (error) {
      console.error('Error processing image:', error);
      throw error;
    }
  }

function updateMaximaCode(code){
    console.log(code.minimaCode.reply)
    codeField.innerHtml = code
}