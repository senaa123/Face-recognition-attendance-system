import os
import pickle

import cv2
import numpy as np


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CASCADE_PATH = os.path.join(DATA_DIR, "haarcascade_frontalface_default.xml")
NAMES_PATH = os.path.join(DATA_DIR, "names.pkl")
FACES_DATA_PATH = os.path.join(DATA_DIR, "faces_data.pkl")

MAX_FACE_SAMPLES = 100
CAPTURE_EVERY_N_FRAMES = 10
FACE_SIZE = (50, 50)


def load_names():
    if not os.path.exists(NAMES_PATH):
        return []

    with open(NAMES_PATH, "rb") as f:
        names = pickle.load(f)

    return list(names)


def load_faces(expected_width):
    if not os.path.exists(FACES_DATA_PATH):
        return None

    with open(FACES_DATA_PATH, "rb") as f:
        faces = pickle.load(f)

    faces = np.asarray(faces)

    # Old broken data may contain names in faces_data.pkl. Face data must be
    # numeric and two-dimensional so KNN receives rows of flattened images.
    if faces.ndim != 2 or not np.issubdtype(faces.dtype, np.number):
        print("Warning: data/faces_data.pkl is invalid and will be replaced.")
        return None

    if faces.shape[1] != expected_width:
        print("Warning: existing face data has a different shape and will be replaced.")
        return None

    return faces


def save_face_data(name, new_faces):
    face_width = new_faces.shape[1]
    names = load_names()
    existing_faces = load_faces(face_width)

    if existing_faces is None:
        names = []
        all_faces = new_faces
    else:
        if len(names) != len(existing_faces):
            usable_count = min(len(names), len(existing_faces))
            print("Warning: names and face data counts did not match. Keeping the matching rows only.")
            names = names[:usable_count]
            existing_faces = existing_faces[:usable_count]

        all_faces = np.append(existing_faces, new_faces, axis=0)

    names.extend([name] * len(new_faces))

    with open(NAMES_PATH, "wb") as f:
        pickle.dump(names, f)

    with open(FACES_DATA_PATH, "wb") as f:
        pickle.dump(all_faces, f)


os.makedirs(DATA_DIR, exist_ok=True)

facedetect = cv2.CascadeClassifier(CASCADE_PATH)
if facedetect.empty():
    raise SystemExit("Could not load Haar cascade from " + CASCADE_PATH)

video = cv2.VideoCapture(0)
if not video.isOpened():
    raise SystemExit("Could not open webcam.")

faces_data = []
frame_count = 0

name = input("Enter your name: ").strip()
if not name:
    video.release()
    cv2.destroyAllWindows()
    raise SystemExit("Name cannot be empty.")

while True:
    ret, frame = video.read()
    if not ret:
        print("Could not read frame from webcam.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        crop_image = frame[y:y + h, x:x + w, :]
        resized_image = cv2.resize(crop_image, FACE_SIZE)

        if len(faces_data) < MAX_FACE_SAMPLES and frame_count % CAPTURE_EVERY_N_FRAMES == 0:
            faces_data.append(resized_image)

        frame_count += 1
        cv2.putText(frame, str(len(faces_data)), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 255), 1)

    cv2.imshow("Video Frame", frame)
    k = cv2.waitKey(1)

    if k == ord("q") or len(faces_data) == MAX_FACE_SAMPLES:
        break

video.release()
cv2.destroyAllWindows()

if len(faces_data) == 0:
    raise SystemExit("No face samples were collected. Nothing was saved.")

faces_data = np.asarray(faces_data)
faces_data = faces_data.reshape(len(faces_data), -1)
save_face_data(name, faces_data)

print(f"Saved {len(faces_data)} face samples for {name}.")
