from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime 
from win32com.client import Dispatch

def speak(str1):
     speak = Dispatch(("SAPI.SpVoice"))
     speak.Speak(str1)

video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

with open('data/names.pkl', 'rb') as f:
      Labels = pickle.load(f)
with open('data/faces_data.pkl', 'rb') as f:
      faces = pickle.load(f)      

knn=KNeighborsClassifier(n_neighbors=5)
knn.fit(faces, Labels)

img_background = cv2.imread("hi.png")

COL_NAMES = ['NAME', 'TIME']

while True:
    ret, frame =video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
    faces = facedetect.detectMultiScale(gray, 1.3 ,5)   
    for(x,y,w,h) in faces:
       crop_image = frame[y:y+h, x:x+w, :]
       resized_image = cv2.resize(crop_image, (50, 50)).flatten().reshape(1, -1)
       output = knn.predict(resized_image)
       ts = time.time()
       date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
       timestamp = datetime.fromtimestamp(ts).strftime("%H-%M-%S")
       exist = os.path.isfile("Attendance/Attendance_" +date+".csv")
       cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 0, 255), 1)
       cv2.rectangle(frame, (x,y), (x+w, y+h), (50, 50, 255), 2)
       cv2.rectangle(frame, (x,y-40), (x+w, y), (50, 50, 255), -1)
       cv2.putText(frame, str(output[0]), (x,y-15), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 1)
       cv2.rectangle(frame, (x,y), (x+w, y+h), (50, 50, 255), 1) 
       attendance = [str(output[0]), str(timestamp)]
    img_background[162:162 + 480, 55:55 + 640] = frame
    cv2.imshow("Video Frame", img_background)    
    k = cv2.waitKey(1)
    if k == ord('o'):
        speak("Attendance Taken...")
        time.sleep(5)
        if exist:
            with open("Attendance/Attendance_" +date+".csv", "+a") as csvfile:
                  writer = csv.writer(csvfile)
                  writer.writerow(attendance)
            csvfile.close() 
        else:
             with open("Attendance/Attendance_" +date+".csv", "+a") as csvfile:
                  writer = csv.writer(csvfile)
                  writer.writerow(COL_NAMES)
                  writer.writerow(attendance)
             csvfile.close() 
    
    if k == ord('q'):
        break
video.release()
cv2.destroyAllWindows()

