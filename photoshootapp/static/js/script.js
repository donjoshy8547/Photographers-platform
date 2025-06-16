const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const upload = document.getElementById('upload');
const cropBtn = document.getElementById('crop');
const brightnessIncreaseBtn = document.getElementById('brightness-increase');
const brightnessDecreaseBtn = document.getElementById('brightness-decrease');
const contrastIncreaseBtn = document.getElementById('contrast-increase');
const contrastDecreaseBtn = document.getElementById('contrast-decrease');
const downloadBtn = document.getElementById('download');

let image = new Image();
let isCropping = false;
let startX, startY, endX, endY;

// Load image onto the canvas
upload.addEventListener('change', (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      image.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }
});

image.onload = () => {
  canvas.width = image.width;
  canvas.height = image.height;
  ctx.drawImage(image, 0, 0);
};

// Mouse events for cropping
canvas.addEventListener('mousedown', (event) => {
  isCropping = true;
  startX = event.offsetX;
  startY = event.offsetY;
});

canvas.addEventListener('mousemove', (event) => {
  if (isCropping) {
    endX = event.offsetX;
    endY = event.offsetY;
    ctx.drawImage(image, 0, 0);
    ctx.strokeStyle = 'red';
    ctx.lineWidth = 2;
    ctx.strokeRect(startX, startY, endX - startX, endY - startY);
  }
});

canvas.addEventListener('mouseup', () => {
  isCropping = false;
});

// Perform cropping
cropBtn.addEventListener('click', () => {
  const cropWidth = endX - startX;
  const cropHeight = endY - startY;
  const croppedImageData = ctx.getImageData(startX, startY, cropWidth, cropHeight);

  canvas.width = cropWidth;
  canvas.height = cropHeight;
  ctx.putImageData(croppedImageData, 0, 0);

  image.src = canvas.toDataURL();
});

// Adjust brightness
function adjustBrightness(value) {
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const data = imageData.data;

  for (let i = 0; i < data.length; i += 4) {
    data[i] = Math.min(255, Math.max(0, data[i] + value)); // Red
    data[i + 1] = Math.min(255, Math.max(0, data[i + 1] + value)); // Green
    data[i + 2] = Math.min(255, Math.max(0, data[i + 2] + value)); // Blue
  }

  ctx.putImageData(imageData, 0, 0);
}

brightnessIncreaseBtn.addEventListener('click', () => adjustBrightness(20));
brightnessDecreaseBtn.addEventListener('click', () => adjustBrightness(-20));

// Adjust contrast
function adjustContrast(value) {
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const data = imageData.data;

  const factor = (259 * (value + 255)) / (255 * (259 - value));
  for (let i = 0; i < data.length; i += 4) {
    data[i] = Math.min(255, Math.max(0, factor * (data[i] - 128) + 128)); // Red
    data[i + 1] = Math.min(255, Math.max(0, factor * (data[i + 1] - 128) + 128)); // Green
    data[i + 2] = Math.min(255, Math.max(0, factor * (data[i + 2] - 128) + 128)); // Blue
  }

  ctx.putImageData(imageData, 0, 0);
}

contrastIncreaseBtn.addEventListener('click', () => adjustContrast(20));
contrastDecreaseBtn.addEventListener('click', () => adjustContrast(-20));

// Download the edited image
downloadBtn.addEventListener('click', () => {
  const link = document.createElement('a');
  link.download = 'edited_image.png';
  link.href = canvas.toDataURL();
  link.click();
});
