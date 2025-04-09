const videoElement = document.getElementById('video');
const canvasElement = document.getElementById('canvas');
const canvasCtx = canvasElement.getContext('2d');
const startButton = document.getElementById('start-btn');
const stopButton = document.getElementById('stop-btn');
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const fpsDisplay = document.getElementById('fps');
const resolutionDisplay = document.getElementById('resolution');
const framesCountDisplay = document.getElementById('frames-count');
const overlay = document.getElementById('overlay');
const overlayText = document.getElementById('overlay-text');

// Image upload elements
const uploadArea = document.getElementById('upload-area');
const uploadInput = document.getElementById('image-upload');
const previewContainer = document.getElementById('preview-container');
const previewImage = document.getElementById('preview-image');
const removeImageButton = document.getElementById('remove-image');
const uploadStatus = document.getElementById('upload-status');
const notification = document.getElementById('notification');

let websocket = null;
let mediaStream = null;
let isStreaming = false;
let frameCount = 0;
let lastFrameTime = 0;
let frameInterval = null;
const targetFps = 30;
const frameDelay = 1000 / targetFps;

// Store the selected image file
let selectedImageFile = null;
const apiBaseUrl = 'http://localhost:8000';

// Initialize webcam
async function initializeWebcam() {
    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({
            video: { width: 640, height: 480 },
            audio: false
        });
        
        videoElement.srcObject = mediaStream;
        
        // Wait for video to be ready
        videoElement.onloadedmetadata = () => {
            canvasElement.width = videoElement.videoWidth;
            canvasElement.height = videoElement.videoHeight;
            resolutionDisplay.textContent = `${videoElement.videoWidth}x${videoElement.videoHeight}`;
            startButton.disabled = false;
        };
    } catch (error) {
        console.error('Error accessing webcam:', error);
        showNotification('Error accessing webcam. Please check permissions.', true);
    }
}

// Connect to WebSocket server
function connectWebSocket() {
    websocket = new WebSocket('ws://localhost:8000/ws');
    
    websocket.onopen = () => {
        statusIndicator.classList.add('connected');
        statusText.textContent = 'Connected';
        startStreaming();
    };
    
    websocket.onclose = () => {
        statusIndicator.classList.remove('connected');
        statusText.textContent = 'Disconnected';
        stopStreaming();
    };
    
    websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        statusText.textContent = 'Connection Error';
        stopStreaming();
        showNotification('WebSocket connection error', true);
    };
    
    websocket.onmessage = (event) => {
        const message = event.data;
        // check here amrit
        // Display server message
        overlayText.textContent = message;
        overlay.classList.add('active');
        
        // If "Pull" is detected and we have an image, upload it
        if (message === 'Pull' && selectedImageFile) {
            uploadImage();
        }
        
        // Stop streaming when receiving "Push" or "Pull"
        if (message === 'Push' || message === 'Pull') {
            stopStreaming();
            websocket.close();
        }
        
        // Hide overlay after 3 seconds
        setTimeout(() => {
            overlay.classList.remove('active');
        }, 3000);
    };
}

// Capture and send frames
function captureAndSendFrame() {
    if (!isStreaming || !websocket || websocket.readyState !== WebSocket.OPEN) return;
    
    // Calculate FPS
    const now = performance.now();
    const delta = now - lastFrameTime;
    lastFrameTime = now;
    
    if (delta > 0) {
        const currentFps = Math.round(1000 / delta);
        fpsDisplay.textContent = currentFps;
    }
    
    // Draw video frame to canvas
    canvasCtx.drawImage(videoElement, 0, 0);
    
    // Convert canvas to blob and send via WebSocket
    canvasElement.toBlob((blob) => {
        if (blob && websocket && websocket.readyState === WebSocket.OPEN) {
            websocket.send(blob);
            frameCount++;
            framesCountDisplay.textContent = frameCount;
        }
    }, 'image/jpeg', 0.8);
}

// Start streaming
function startStreaming() {
    if (isStreaming) return;
    
    isStreaming = true;
    frameCount = 0;
    framesCountDisplay.textContent = '0';
    lastFrameTime = performance.now();
    
    // Add recording class for the pulse animation
    stopButton.classList.add('recording');
    
    // Send frames at target FPS
    frameInterval = setInterval(captureAndSendFrame, frameDelay);
    
    startButton.disabled = true;
    stopButton.disabled = false;
}

// Stop streaming
function stopStreaming() {
    if (!isStreaming) return;
    
    isStreaming = false;
    
    if (frameInterval) {
        clearInterval(frameInterval);
        frameInterval = null;
    }
    
    stopButton.classList.remove('recording');
    
    startButton.disabled = false;
    stopButton.disabled = true;
}

// Upload image to the server
async function uploadImage() {
    if (!selectedImageFile) {
        showNotification('No image selected', true);
        return;
    }
    
    uploadStatus.textContent = 'Uploading...';
    
    try {
        const formData = new FormData();
        formData.append('file', selectedImageFile);

            await sleep(2000); // Pause for 2 seconds (2000 milliseconds)

        
        const response = await fetch(`${apiBaseUrl}/store-image`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}`);
        }
        
        const result = await response.json();
        uploadStatus.textContent = 'Upload successful';
        showNotification('Image uploaded successfully!');
        console.log('Upload result:', result);
        
    } catch (error) {
        console.error('Error uploading image:', error);
        uploadStatus.textContent = 'Upload failed';
        showNotification('Failed to upload image', true);
    }
}

// Handle file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Check if file is an allowed image type
    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        showNotification('Invalid file type. Please select JPG, PNG, or WebP image.', true);
        return;
    }
    
    selectedImageFile = file;
    
    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewContainer.classList.add('active');
        uploadStatus.textContent = `Selected: ${file.name}`;
    };
    reader.readAsDataURL(file);
}

// Show notification
function showNotification(message, isError = false) {
    notification.textContent = message;
    notification.className = 'notification';
    
    if (isError) {
        notification.classList.add('error');
    }
    
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// Handle start button click
startButton.addEventListener('click', () => {
    if (mediaStream) {
        connectWebSocket();
    } else {
        initializeWebcam().then(connectWebSocket);
    }
});

// Handle stop button click
stopButton.addEventListener('click', () => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.close();
    }
    stopStreaming();
});

// Handle file input change
uploadInput.addEventListener('change', handleFileSelect);

// Handle drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    
    if (e.dataTransfer.files.length) {
        uploadInput.files = e.dataTransfer.files;
        handleFileSelect({ target: { files: e.dataTransfer.files } });
    }
});

// Handle remove image button click
removeImageButton.addEventListener('click', () => {
    previewContainer.classList.remove('active');
    uploadInput.value = '';
    selectedImageFile = null;
    uploadStatus.textContent = 'Ready';
});

// Initialize webcam on page load
window.addEventListener('load', initializeWebcam);

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
//   async function myFunction() {
//     console.log("Start");
//     await sleep(2000); // Pause for 2 seconds (2000 milliseconds)
//     console.log("After 2 seconds");
//     await sleep(1000); // Pause for 1 second
//     console.log("After 1 more second");
//     console.log("End");
//   }