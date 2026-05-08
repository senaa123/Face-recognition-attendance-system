# Face Recognition Attendance System

A beginner-friendly real-time attendance system using a webcam, OpenCV face detection, KNN recognition, and a Streamlit dashboard.

Users register face samples with `add_faces.py`, the recognition script marks attendance in a daily CSV file, and `app.py` displays the current day's records.

## Features

- Register face samples from a webcam
- Store names in `data/names.pkl`
- Store flattened face image data in `data/faces_data.pkl`
- Recognize registered users with KNN
- Reject likely unknown faces using a distance threshold
- Prevent duplicate attendance for the same person on the same day
- Save attendance to `Attendance/Attendance_DD-MM-YYYY.csv`
- View today's attendance in Streamlit

## Project Structure

```text
Face-recognition-attendance-system/
|-- add_faces.py
|-- test.py
|-- app.py
|-- requirements.txt
|-- data/
|   |-- haarcascade_frontalface_default.xml
|   |-- faces_data.pkl       # ignored by Git
|   `-- names.pkl            # ignored by Git
|-- Attendance/
|   |-- .gitkeep
|   `-- Attendance_DD-MM-YYYY.csv  # ignored by Git
|-- hi.png
`-- README.md
```

## Setup

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

Register a face:

```powershell
python add_faces.py
```

Start recognition and attendance marking:

```powershell
python test.py
```

Press `o` to mark attendance for the recognized person. Press `q` to quit.

Open the dashboard:

```powershell
streamlit run app.py
```

## Unknown Face Threshold

`test.py` uses `UNKNOWN_THRESHOLD = 4500` with `knn.kneighbors()` to decide whether a face is too far from saved samples.

Tune this value in `test.py`:

- Increase it if registered users are shown as `Unknown`
- Decrease it if unknown people are accepted as registered users

Lighting, camera quality, and the number of samples can affect this threshold.

## Git Ignored Data

Private biometric data and generated attendance files are ignored by Git:

- `data/faces_data.pkl`
- `data/names.pkl`
- `Attendance/*.csv`

The Haar cascade file remains tracked because the project needs it to detect faces.
