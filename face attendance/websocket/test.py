import asyncio
import cv2
import numpy as np
import websockets
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
import os

# CSV file name for storing face data
f_name = 'face_data.csv'

# Load and process the CSV file
try:
    if os.path.isfile(f_name):
        data = pd.read_csv(f_name)
        X = np.array([np.array(eval(encoding)) for encoding in data['encoding']])
        Y = data['name'].values

        if X.shape[1] != 49152:
            raise ValueError(f"Expected 12,288 dimensions for encodings, but got {X.shape[1]}")
    else:
        raise FileNotFoundError(f"{f_name} not found!")

except Exception as e:
    print(f"Error loading or processing data: {e}")
    exit()

# Train the KNN model
model = KNeighborsClassifier(n_neighbors=1)
model.fit(X, Y)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

async def recognize_faces(websocket, path):
    async for message in websocket:
        try:
            nparr = np.frombuffer(message, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            faces = face_cascade.detectMultiScale(frame, 1.5, 5)
            X_test = []

            for (x, y, w, h) in faces:
                im_face = frame[y:y + h, x:x + w]
                im_face = cv2.resize(im_face, (128, 128))
                face_encoding = im_face.flatten()
                X_test.append(face_encoding)

            if len(X_test) > 0:
                predictions = model.predict(np.array(X_test))
                response = ','.join(predictions)
            else:
                response = "No face detected."

            await websocket.send(response)

        except Exception as e:
            await websocket.send(f"Error: {str(e)}")

# Start the WebSocket server
async def main():
    async with websockets.serve(recognize_faces, "localhost", 8766):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
