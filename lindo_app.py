import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration, VideoProcessorBase
import cv2
import requests
import base64
import pandas as pd
import time
from datetime import datetime
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import numpy as np

# --- הגדרות ליבה ---
API_KEY = "AIzaSyCViOTuoBmPtAcRTT_8zmmQYT-Z4pn6C3U"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
EMAIL_SENDER = "adawiavihai@gmail.com"
EMAIL_RECEIVER = "adawiavihai@gmail.com"
EMAIL_PASSWORD = "ykzlkfyvfzqudxpg" 

st.set_page_config(page_title="Lindo Guard Elite", layout="wide", page_icon="🛡️")

# אתחול Session State
if 'history' not in st.session_state: st.session_state.history = []
if 'alerts_count' not in st.session_state: st.session_state.alerts_count = 0
if 'health_alerts' not in st.session_state: st.session_state.health_alerts = 0
if 'last_analysis' not in st.session_state: st.session_state.last_analysis = 0

st.markdown(f"<h1>🛡️ LINDO GUARD <span style='font-size: 15px; color: red;'>● AI ACTIVE</span></h1>", unsafe_allow_html=True)

col_left, col_right = st.columns([1.5, 1])

with col_right:
    st.markdown("### 📜 יומן אירועים")
    log_spot = st.empty()
    if st.session_state.history:
        log_spot.table(pd.DataFrame(st.session_state.history).head(10))

with col_left:
    rtc_config = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}, {"urls": ["stun:global.stun.twilio.com:3478"]}]})
    
    class VideoProcessor(VideoProcessorBase):
        def recv(self, frame):
            img = frame.to_ndarray(format="bgr24")
            
            # ניתוח פעם ב-45 שניות כדי לא להעמיס
            curr = time.time()
            if curr - st.session_state.last_analysis > 45:
                st.session_state.last_analysis = curr
                
                # הקטנת התמונה לשיפור מהירות
                small_img = cv2.resize(img, (320, 240))
                _, buffer = cv2.imencode('.jpg', small_img)
                img_b64 = base64.b64encode(buffer).decode('utf-8')
                
                prompt = "Briefly analyze this dog. Is he OK? If jumping on sofa or limping, say 'ALERT' or 'HEALTH'. Answer in Hebrew."
                payload = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
                
                try:
                    res = requests.post(URL, json=payload, timeout=10).json()
                    text = res['candidates'][0]['content']['parts'][0]['text']
                    
                    t_str = datetime.now().strftime("%H:%M")
                    status = "✅ תקין"
                    if "ALERT" in text: status = "🚨 חריגה"
                    elif "HEALTH" in text: status = "🩺 בריאותי"
                    
                    # הזרקת הנתונים לטבלה
                    new_entry = {"זמן": t_str, "מצב": status, "פירוט": text[:50] + "..."}
                    st.session_state.history.insert(0, new_entry)
                except:
                    pass
            
            return frame

    webrtc_streamer(
        key="lindo-final-v5",
        rtc_configuration=rtc_config,
        video_processor_factory=VideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True, # קריטי למניעת תקיעות
    )
