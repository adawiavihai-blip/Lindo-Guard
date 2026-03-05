import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
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

# --- הגדרות ליבה ---
API_KEY = "AIzaSyCViOTuoBmPtAcRTT_8zmmQYT-Z4pn6C3U"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
EMAIL_SENDER = "adawiavihai@gmail.com"
EMAIL_RECEIVER = "adawiavihai@gmail.com"
EMAIL_PASSWORD = "ykzlkfyvfzqudxpg" 

st.set_page_config(page_title="Lindo Guard Elite", layout="wide", page_icon="🛡️")

# עיצוב CSS מתקדם
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .metric-card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.03); text-align: center; border-top: 5px solid #1565C0; }
    .check-list-container { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
    .live-dot { height: 10px; width: 10px; background-color: #ff4b4b; border-radius: 50%; display: inline-block; margin-right: 5px; animation: blink 1s infinite; }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

# אתחול Session State
if 'history' not in st.session_state: st.session_state.history = []
if 'visual_history' not in st.session_state: st.session_state.visual_history = []
if 'alerts_count' not in st.session_state: st.session_state.alerts_count = 0
if 'health_alerts' not in st.session_state: st.session_state.health_alerts = 0

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

# --- דשבורד ראשי ---
st.markdown(f"<h1>🛡️ LINDO GUARD <span style='font-size: 15px; vertical-align: middle;'><span class='live-dot'></span>WEB STREAMING</span></h1>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("🚨 חריגות משמעת", st.session_state.alerts_count)
with c2: st.metric("🩺 מדדי בריאות", st.session_state.health_alerts)
with c3: st.metric("⏱️ קצב סריקה", "60 שנ'")
with c4: st.metric("🛡️ סטטוס", "מחובר")

st.divider()

col_left, col_right = st.columns([1.6, 1])

with col_right:
    st.markdown("### 📸 תיעוד חזותי")
    gallery_spot = st.empty()
    st.divider()
    st.markdown("### 📜 יומן ניתוח חכם")
    log_spot = st.empty()
    if st.session_state.history:
        log_spot.table(pd.DataFrame(st.session_state.history).head(10))

with col_left:
    st.markdown("### 🎥 שידור חי מהמצלמה")
    
    # הגדרות חיבור משופרות לעקיפת חסימות (STUN Servers)
    rtc_config = RTCConfiguration(
        {"iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]},
            {"urls": ["stun:stun1.l.google.com:19302"]},
            {"urls": ["stun:stun2.l.google.com:19302"]},
            {"urls": ["stun:stun3.l.google.com:19302"]},
            {"urls": ["stun:stun4.l.google.com:19302"]},
            {"urls": ["stun:global.stun.twilio.com:3478"]}
        ]}
    )
    
    # הפעלת המצלמה - מופיע פעם אחת בלבד!
    webrtc_ctx = webrtc_streamer(
        key="lindo-guard-v3-final",
        rtc_configuration=rtc_config,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="check-list-container">
        <h4 style="color: #1565C0; margin-top: 0;">🔍 פרוטוקול בדיקות AI Elite</h4>
        <p>✅ ניתוח תנועה, משמעת בית, מעקב תזונה וסינון אנושי.</p>
    </div>
    """, unsafe_allow_html=True)

# לוגיקת AI (רצה כשוידאו פעיל)
if webrtc_ctx.state.playing:
    st.toast("המערכת מנתחת את השידור החי...")
