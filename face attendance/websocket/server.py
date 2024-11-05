import asyncio
import websockets
import cv2
import numpy as np
import pandas as pd
import os
import struct
import json
from sklearn.neighbors import KNeighborsClassifier
from datetime import datetime

f_name = "face_data.csv"
knn = KNeighborsClassifier(n_neighbors=3)
ENCODING_THRESHOLD = 30

# Function to write face data to CSV and trigger model training at the threshold
def write(name, encoding):
    # Load existing data or create new DataFrame
    df = pd.read_csv(f_name) if os.path.isfile(f_name) else pd.DataFrame(columns=["name", "encoding", "timestamp"])

    # Filter encodings to only save if under threshold
    user_encodings = df[df["name"] == name]
    if len(user_encodings) < ENCODING_THRESHOLD:
        new_entry = pd.DataFrame({
            "name": [name],
            "encoding": [json.dumps(encoding.tolist())],  # Store encoding as JSON
            "timestamp": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        })
        df = pd.concat([df, new_entry], ignore_index=True, sort=False)
        df.to_csv(f_name, index=False)

        # Check if we’ve hit the threshold of 30 encodings for training
        user_encodings = df[df["name"] == name]
        if len(user_encodings) == ENCODING_THRESHOLD:
            train_model(df, name)  # Train model when threshold is met

# Function to train the KNN model on 30 encodings for the specified user
def train_model(df, name):
    user_data = df[df["name"] == name]
    X = np.array([np.array(json.loads(enc)) for enc in user_data["encoding"].values])  # JSON decoding
    y = user_data["name"].values
    knn.fit(X, y)
    print(f"Model trained with 30 encodings for {name}")

# Process incoming WebSocket messages
async def process_message(websocket, message):
    try:
        # Unpack username length
        username_length = struct.unpack('I', message[:4])[0]
        username = message[4:4 + username_length].decode('utf-8')
        image_data = message[4 + username_length:]

        # Convert image data to numpy array and process it
        image_array = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        # Face detection and encoding
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            face = img[y:y+h, x:x+w]
            face_resized = cv2.resize(face, (128, 128))
            encoding = face_resized.flatten()
            write(username, encoding)  # Save encoding and trigger training if threshold is met
            await websocket.send(f"Face data for {username} saved successfully.")
        else:
            await websocket.send("No face detected.")
    except Exception as e:
        await websocket.send(f"Error processing message: {str(e)}")

# Handle each client connection
async def handle_client(websocket, path):
    async for message in websocket:
        await process_message(websocket, message)

# Main function to start the WebSocket server
async def main():
    async with websockets.serve(handle_client, "localhost", 8767):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
