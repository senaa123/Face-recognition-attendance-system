import os
import csv
import time
import pickle
from datetime import datetime

import cv2
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

try:
    from win32com.client import Dispatch
except ImportError:
    Dispatch = None


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ATTENDANCE_DIR = os.path.join(BASE_DIR, "Attendance")
CASCADE_PATH = os.path.join(DATA_DIR, "haarcascade_frontalface_default.xml")
NAMES_PATH = os.path.join(DATA_DIR, "names.pkl")
FACES_DATA_PATH = os.path.join(DATA_DIR, "faces_data.pkl")
BACKGROUND_PATH = os.path.join(BASE_DIR, "hi.png")

COL_NAMES = ["NAME", "TIME"]
FACE_SIZE = (50, 50)

# This value depends on camera quality, lighting, and saved samples.
# If known people are shown as Unknown, increase it a little. If unknown
# people are accepted as registered users, decrease it.
UNKNOWN_THRESHOLD = 4500


def speak(message):
    print(message)
    if Dispatch is None:
        return

    try:
        speaker = Dispatch("SAPI.SpVoice")
        speaker.Speak(message)
    except Exception:
        pass


def today_attendance_file():
    date = datetime.now().strftime("%d-%m-%Y")
    return os.path.join(ATTENDANCE_DIR, "Attendance_" + date + ".csv")


def attendance_already_marked(file_path, name):
    if not os.path.exists(file_path):
        return False

    with open(file_path, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row.get("NAME") == name:
                return True

    return False


def mark_attendance(name):
    if name == "Unknown":
        speak("Unknown person. Attendance not marked.")
        return "Unknown person. Attendance not marked."

    attendance_file = today_attendance_file()

    if attendance_already_marked(attendance_file, name):
        speak("Attendance already marked")
        return "Attendance already marked"

    timestamp = datetime.now().strftime("%H:%M:%S")
    file_has_data = os.path.exists(attendance_file) and os.path.getsize(attendance_file) > 0

    with open(attendance_file, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_has_data:
            writer.writerow(COL_NAMES)
        writer.writerow([name, timestamp])

    speak("Attendance Taken")
    return "Attendance Taken"


def load_training_data():
    if not os.path.exists(NAMES_PATH) or not os.path.exists(FACES_DATA_PATH):
        raise SystemExit("No saved face data found. Run add_faces.py first.")

    with open(NAMES_PATH, "rb") as f:
        labels = list(pickle.load(f))

    with open(FACES_DATA_PATH, "rb") as f:
        faces = np.asarray(pickle.load(f))

    if faces.ndim != 2 or not np.issubdtype(faces.dtype, np.number):
        raise SystemExit(FACES_DATA_PATH + " is invalid. Run add_faces.py again to recreate it.")

    if len(labels) != len(faces):
        usable_count = min(len(labels), len(faces))
        labels = labels[:usable_count]
        faces = faces[:usable_count]
        print("Warning: labels and face rows did not match. Using the matching rows only.")

    if len(labels) == 0:
        raise SystemExit("No usable face data found. Run add_faces.py first.")

    return labels, faces


os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ATTENDANCE_DIR, exist_ok=True)

facedetect = cv2.CascadeClassifier(CASCADE_PATH)
if facedetect.empty():
    raise SystemExit("Could not load Haar cascade from " + CASCADE_PATH)

labels, faces_data = load_training_data()

knn = KNeighborsClassifier(n_neighbors=min(5, len(labels)))
knn.fit(faces_data, labels)

video = cv2.VideoCapture(0)
if not video.isOpened():
    raise SystemExit("Could not open webcam.")

img_background = cv2.imread(BACKGROUND_PATH)
status_message = "Press o to mark attendance, q to quit"
recognized_name = None

while True:
    ret, frame = video.read()
    if not ret:
        print("Could not read frame from webcam.")
        break

    recognized_name = None
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detected_faces = facedetect.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in detected_faces:
        crop_image = frame[y:y + h, x:x + w, :]
        resized_image = cv2.resize(crop_image, FACE_SIZE).flatten().reshape(1, -1)

        distances, _ = knn.kneighbors(resized_image, n_neighbors=1)
        nearest_distance = distances[0][0]

        if nearest_distance > UNKNOWN_THRESHOLD:
            recognized_name = "Unknown"
        else:
            recognized_name = str(knn.predict(resized_image)[0])

        box_color = (0, 0, 255) if recognized_name == "Unknown" else (50, 50, 255)
        cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
        cv2.rectangle(frame, (x, y - 40), (x + w, y), box_color, -1)
        cv2.putText(frame, recognized_name, (x, y - 15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
        cv2.putText(frame, "Distance: " + str(round(nearest_distance, 2)), (x, y + h + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

    cv2.putText(frame, status_message, (20, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    if img_background is not None and img_background.shape[0] >= 642 and img_background.shape[1] >= 695:
        display_frame = img_background.copy()
        display_frame[162:162 + 480, 55:55 + 640] = frame
    else:
        display_frame = frame

    cv2.imshow("Video Frame", display_frame)
    k = cv2.waitKey(1)

    if k == ord("o"):
        if recognized_name is None:
            status_message = "No face detected"
            speak(status_message)
        else:
            status_message = mark_attendance(recognized_name)
        time.sleep(1)

    if k == ord("q"):
        break

video.release()
cv2.destroyAllWindows()
