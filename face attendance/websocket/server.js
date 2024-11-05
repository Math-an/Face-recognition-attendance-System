const WebSocket = require('ws');
const ws = new WebSocket('ws://localhost:8765'); // WebSocket server address

ws.on('open', () => {
    console.log("WebSocket connection established.");
    sendImagesFromLocalStorage(); // Send images after connection is open
});

ws.on('message', (message) => {
    console.log("Message from server: ", message);
});

ws.on('error', (error) => {
    console.error("WebSocket error: ", error);
});

// Function to send images from local storage to the server
function sendImagesFromLocalStorage() {
    const faceData = JSON.parse(localStorage.getItem('faceData')); // Retrieve face data (base64)

    if (faceData && Array.isArray(faceData)) {
        faceData.forEach((image, index) => {
            // Convert base64 image data to binary
            const byteString = atob(image.split(',')[1]); // Decode base64
            const ab = new Uint8Array(byteString.length);
            
            for (let i = 0; i < byteString.length; i++) {
                ab[i] = byteString.charCodeAt(i);
            }

            // Send binary image data to the server
            ws.send(ab.buffer);
            console.log(`Image ${index + 1} sent to server.`);
        });
        console.log("All images sent to the server.");
    } else {
        console.error("No face data found in local storage.");
    }
}
