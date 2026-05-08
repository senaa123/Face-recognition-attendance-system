# Face Recognition Attendance System

A real-time face recognition attendance system built using Python, OpenCV, and Machine Learning.  
The system captures face data through a webcam, trains a K-Nearest Neighbors classifier, recognizes registered users in real time, and records attendance automatically into CSV files.

## Features

- Real-time face detection using OpenCV Haar Cascade
- Face data collection through webcam
- Face recognition using K-Nearest Neighbors classification
- Automatic attendance marking with name and timestamp
- Daily attendance CSV file generation
- Simple Streamlit dashboard to view attendance records
- Voice notification when attendance is marked

## Tech Stack

- Python
- OpenCV
- NumPy
- scikit-learn
- Pandas
- Streamlit
- Pickle
- pywin32

## Project Structure

```text
Face-recognition-attendance-system/
│
├── add_faces.py                  # Captures and stores face data
├── test.py                       # Runs real-time face recognition and marks attendance
├── app.py                        # Streamlit app to display attendance records
│
├── data/
│   ├── haarcascade_frontalface_default.xml
│   ├── faces_data.pkl
│   └── names.pkl
│
├── Attendance/
│   └── Attendance_DD-MM-YYYY.csv
│
├── hi.png                        # Background image for recognition UI
└── README.md