import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration, VideoProcessorBase
import cv2
import requests
import base64
import pandas as pd
import time
from datetime import datetime
import numpy as np

# --- הגדרות ליבה ---
API_KEY = "AIzaSyCViOTuoBmPtAcRTT_8zmmQYT-Z4pn6C3U"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

st.set_page_config(page_title="Lindo Guard Pro", layout="wide")

if 'history' not in st.session_state: st.session_state.history = []
if 'last_proc' not in st.session_state: st.session_state.last_proc = 0

st.title("🛡️ Lindo Guard - AI Live Monitor")

# הגדרות חיבור חזקות (עוקף חסימות ראוטר)
RTC_CONFIG = RTCConfiguration(
    {"iceServers": [
        {"urls": ["stun:stun.l.google.com:19302"]},
        {"urls": ["stun:stun1.l.google.com:19302"]},
        {"urls": ["stun:stun.l.google.com:19302", "stun:global.stun.twilio.com:3478?transport=udp"]}
    ]}
)

col_left, col_right = st.columns([2, 1])

with col_right:
    st.subheader("📜 יומן אירועים")
    log_area = st.empty()
    if st.session_state.history:
        log_area.table(pd.DataFrame(st.session_state.history))

with col_left:
    class VideoProcessor(VideoProcessorBase):
        def recv(self, frame):
            img = frame.to_ndarray(format="bgr24")
            
            # ניתוח פעם ב-30 שניות, תמונה קטנה מאוד כדי לא לתקוע את הוידאו
            now = time.time()
            if now - st.session_state.last_proc > 30:
                st.session_state.last_proc = now
                
                # כיווץ תמונה מקסימלי למהירות
                small = cv2.resize(img, (160, 120))
                _, buff = cv2.imencode('.jpg', small)
                b64 = base64.b64encode(buff).decode('utf-8')
                
                payload = {"contents": [{"parts": [
                    {"text": "Analyze dog: Status (OK/ALERT/HEALTH) + Short Hebrew reason."},
                    {"inline_data": {"mime_type": "image/jpeg", "data": b64}}
                ]}]}
                
                try:
                    r = requests.post(URL, json=payload, timeout=5).json()
                    ans = r['candidates'][0]['content']['parts'][0]['text']
                    st.session_state.history.insert(0, {"זמן": datetime.now().strftime("%H:%M"), "ניתוח": ans})
                except: pass
            
            return frame

    webrtc_streamer(
        key="lindo-final-safe",
        rtc_configuration=RTC_CONFIG,
        video_processor_factory=VideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True, # מונע מהוידאו לקפוא בזמן שה-AI חושב
    )
