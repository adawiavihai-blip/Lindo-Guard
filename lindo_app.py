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
if 'last_analysis_time' not in st.session_state: st.session_state.last_analysis_time = 0

def send_email_alert(reason, time_str, category):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = f"🚨 {category} - Lindo Guard"
        body = f"אביחי, זוהתה חריגה במערכת:\nזמן: {time_str}\nתיאור: {reason}"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except: pass

st.markdown(f"<h1>🛡️ LINDO GUARD <span style='font-size: 15px; color: red;'>● LIVE AI</span></h1>", unsafe_allow_html=True)

# מדדים
c1, c2, c3 = st.columns(3)
with c1: st.metric("🚨 חריגות משמעת", st.session_state.alerts_count)
with c2: st.metric("🩺 מדדי בריאות", st.session_state.health_alerts)
with c3: st.metric("📡 סטטוס AI", "סורק...")

col_left, col_right = st.columns([1.5, 1])

with col_right:
    st.markdown("### 📜 יומן אירועים")
    log_spot = st.empty()
    if st.session_state.history:
        log_spot.table(pd.DataFrame(st.session_state.history).head(10))

with col_left:
    rtc_config = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}, {"urls": ["stun:global.stun.twilio.com:3478"]}]})
    
    # פונקציית עיבוד הוידאו
    class VideoProcessor(VideoProcessorBase):
        def recv(self, frame):
            img = frame.to_ndarray(format="bgr24")
            
            # בדיקה אם עברה דקה מהניתוח האחרון
            current_time = time.time()
            if current_time - st.session_state.last_analysis_time > 60:
                st.session_state.last_analysis_time = current_time
                
                # המרה ל-Base64 ושליחה ל-Gemini
                _, buffer = cv2.imencode('.jpg', img)
                img_b64 = base64.b64encode(buffer).decode('utf-8')
                
                prompt = "Analyze this dog. Status: ALERT (discipline), HEALTH (limp/pain), or SAFE. Reason in Hebrew."
                payload = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
                
                try:
                    res = requests.post(URL, json=payload, headers={'Content-Type': 'application/json'}).json()
                    text = res['candidates'][0]['content']['parts'][0]['text']
                    
                    t_str = datetime.now().strftime("%H:%M")
                    status = "✅ תקין"
                    if "ALERT" in text: 
                        status = "🚨 חריגה"
                        st.session_state.alerts_count += 1
                        send_email_alert(text, t_str, status)
                    elif "HEALTH" in text:
                        status = "🩺 בריאותי"
                        st.session_state.health_alerts += 1
                        send_email_alert(text, t_str, status)
                    
                    st.session_state.history.insert(0, {"זמן": t_str, "מצב": status, "פירוט": text})
                except: pass
            
            return frame

    webrtc_streamer(
        key="lindo-final-ai",
        rtc_configuration=rtc_config,
        video_processor_factory=VideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
    )
