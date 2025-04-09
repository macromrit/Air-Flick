# External Imports
from fastapi import FastAPI, HTTPException, File, UploadFile, WebSocket
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import shutil
import os

# CV Imports
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

import time

# Internal Improrts 
from model_helper.model_helper import landmark_buffer, hands, extract_landmarks, classify_gesture
from utils.file_deletion import delete_buffer_files

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


IMAGE_FOLDER = "buffer"
FILE_NAME_BASE = "buffer"
POSSIBLE_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]

# @app.get("/get-image")
# async def get_image():
#     for ext in POSSIBLE_EXTENSIONS:
#         file_path = os.path.join(IMAGE_FOLDER, f"{FILE_NAME_BASE}.{ext}")
#         print(file_path)
#         if os.path.exists(file_path):
#             media_type = f"image/{'jpeg' if ext in ['jpg', 'jpeg'] else ext}"
#             print("SENDING IMAGE BRO")
#             return FileResponse(file_path, media_type=media_type)

#     raise HTTPException(status_code=404, detail="Image not found")

@app.get("/get-image")
async def get_image():
    for ext in POSSIBLE_EXTENSIONS:
        file_path = os.path.join(IMAGE_FOLDER, f"{FILE_NAME_BASE}.{ext}")

        headers = {
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        
        if os.path.exists(file_path):
            media_type = f"image/{'jpeg' if ext in ['jpg', 'jpeg'] else ext}"
            print("SENDING IMAGE BRO")

            return FileResponse(file_path, media_type=media_type, headers=headers)

    return FileResponse(
        "buffer/not_in_buffer.png", 
        media_type="image/png", 
        headers=headers)


@app.post("/store-image")
async def store_image(file: UploadFile = File(...)):
    # clearing buffer file, to upsert the new one
    delete_buffer_files("buffer")
    
    # Get original filename and extension
    filename = file.filename
    file_extension = filename.split(".")[-1].lower()

    # Validate extension (optional)
    if file_extension not in ["jpg", "jpeg", "png", "webp"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Store image with a fixed name like "buffer.<ext>"
    new_filename = f"buffer.{file_extension}"
    file_path = os.path.join(IMAGE_FOLDER, new_filename)

    # Save the file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": "Image stored successfully"}


@app.get("/get-nearest-peer")
async def get_nearest_peer():
    # rerunning the whole script for proper execution
    result = subprocess.run(['python', 'p2p_helper/subscriber.py'], capture_output=True, text=True)
    output = result.stdout.strip().split("\n")[-1]  # Clean the output
    if output == "None":
        raise HTTPException(status_code=404, detail="No peer found!")
    
    print("GOT PEET BRO")
    return {'peer-ip': output}



# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

CONFIRM_BUFFER = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()


    print("CLEARED BUFFERB BOZ!!!")
    # clearing prediction and debounce buffer whenever re-connection happens
    CONFIRM_BUFFER.clear()
    landmark_buffer.clear()

    
    while True:
        try:
            data = await websocket.receive_bytes()

            image = Image.open(BytesIO(data)).convert("RGB")
            frame_rgb = np.array(image)
            results = hands.process(frame_rgb)

            if results.multi_hand_landmarks: # if hands detected
                
                hand_landmarks = results.multi_hand_landmarks[0]
                landmarks = extract_landmarks(hand_landmarks)
                landmark_buffer.append(landmarks)

                if len(landmark_buffer) == 30:
                    gesture_label = classify_gesture(list(landmark_buffer)) or "Collecting..."
                    print(gesture_label)
                    CONFIRM_BUFFER.append(gesture_label)
            
            if CONFIRM_BUFFER.count("Push") > 15 or CONFIRM_BUFFER.count("Pull") > 15:
                confirmed = "Push" if CONFIRM_BUFFER.count("Push") > CONFIRM_BUFFER.count("Pull") else "Pull"
                print("Confirmed", confirmed)
                await websocket.send_text(
                    confirmed
                    ) 

                # clearing prediction and debounce buffer whenever re-connection happens
                CONFIRM_BUFFER.clear()
                landmark_buffer.clear()

                # time.sleep(4)
                    
        except Exception as e:
            print("WebSocket error:", e)
            break
            


if __name__ == "__main__":
    # print(returnNearestPeer())
    ...