import cv2
import numpy as np
import mediapipe as mp
import joblib
from collections import deque

# Load the trained model
model = joblib.load('rf_hand_gesture_model.pkl')


# MediaPipe Hands setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
# mp_drawing = mp.solutions.drawing_utils


# Buffer to store 30 frames of landmarks
landmark_buffer = deque(maxlen=30)


# Function to extract landmarks
def extract_landmarks(hand_landmarks):
    return [[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]


# Function to classify gesture
def classify_gesture(landmarks_seq):
    if len(landmarks_seq) < 30:
        return None  # Not enough frames yet

    # Convert to numpy array
    landmarks_array = np.array(landmarks_seq)  # shape: (30, 21, 3)
    input_data = landmarks_array.flatten().reshape(1, -1)  # shape: (1, 1890)

    # Predict gesture
    prediction = model.predict(input_data)[0]
    return "Push" if prediction == 0 else "Pull"
