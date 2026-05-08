import os
from datetime import datetime

import pandas as pd
import streamlit as st


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ATTENDANCE_DIR = os.path.join(BASE_DIR, "Attendance")

os.makedirs(ATTENDANCE_DIR, exist_ok=True)

today = datetime.now()
date = today.strftime("%d-%m-%Y")
attendance_file = os.path.join(ATTENDANCE_DIR, "Attendance_" + date + ".csv")

st.set_page_config(page_title="Face Recognition Attendance")
st.title("Face Recognition Attendance System")
st.subheader("Today: " + today.strftime("%d %B %Y"))

if os.path.exists(attendance_file):
    try:
        df = pd.read_csv(attendance_file)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=["NAME", "TIME"])

    total_attendance = len(df)

    st.metric("Total attendance count", total_attendance)

    if total_attendance > 0:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No attendance has been recorded today.")
else:
    st.metric("Total attendance count", 0)
    st.warning("No attendance has been recorded today.")
