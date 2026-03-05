import streamlit as st
import cv2
import requests
import json
import base64
import pandas as pd
import time
import numpy as np
from datetime import datetime
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- הגדרות ליבה ---
API_KEY = "AIzaSyAYIB_naC7SB4Tu90Dpp0gWE6X4Esb-loM"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
EMAIL_SENDER = "adawiavihai@gmail.com"
EMAIL_RECEIVER = "adawiavihai@gmail.com"
EMAIL_PASSWORD = "ykzlkfyvfzqudxpg" 

st.set_page_config(page_title="Lindo Guard Elite", layout="wide", page_icon="🛡️")

# עיצוב CSS מתקדם למראה אפליקציה מקצועי
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        text-align: center;
        border-top: 5px solid #1565C0;
    }
    .check-list-container {
        background: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }
    .live-dot {
        height: 10px;
        width: 10px;
        background-color: #ff4b4b;
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
        animation: blink 1s infinite;
    }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

# אתחול Session State
if 'history' not in st.session_state: st.session_state.history = []
if 'visual_history' not in st.session_state: st.session_state.visual_history = []
if 'alerts_count' not in st.session_state: st.session_state.alerts_count = 0
if 'health_alerts' not in st.session_state: st.session_state.health_alerts = 0
if 'cam_on' not in st.session_state: st.session_state.cam_on = True

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

# --- סיידבר ניהול ---
with st.sidebar:
    st.markdown("### 🔐 LINDO COMMAND")
    if st.session_state.cam_on:
        st.button("🔴 נטרל הגנה אקטיבית", on_click=lambda: st.session_state.update({"cam_on": False}), use_container_width=True)
    else:
        st.button("🟢 הפעל הגנה אקטיבית", on_click=lambda: st.session_state.update({"cam_on": True}), use_container_width=True)
    
    st.divider()
    st.markdown("### 📊 דוחות וארכיון")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        st.download_button("📥 ייצא דוח רפואי מלא", data=buffer.getvalue(), file_name=f"Lindo_Report_{datetime.now().strftime('%d-%m')}.xlsx", use_container_width=True)

# --- דשבורד ראשי ---
st.markdown(f"<h1>🛡️ LINDO GUARD <span style='font-size: 15px; vertical-align: middle;'><span class='live-dot'></span>LIVE MONITOR</span></h1>", unsafe_allow_html=True)

# שורת מדדי הייטק
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("🚨 חריגות משמעת", st.session_state.alerts_count)
with c2: st.metric("🩺 מדדי בריאות", st.session_state.health_alerts)
with c3: st.metric("⏱️ קצב סריקה", "60 שנ'")
with c4: st.metric("🛡️ סטטוס הגנה", "פעיל" if st.session_state.cam_on else "מושבת")

st.divider()

col_left, col_right = st.columns([1.6, 1])

with col_right:
    st.markdown("### 📸 תיעוד חזותי")
    gallery_spot = st.empty()
    st.divider()
    st.markdown("### 📜 יומן ניתוח חכם")
    log_spot = st.empty()

with col_left:
    if st.session_state.cam_on:
        video_spot = st.empty()
    else:
        st.error("השידור מושבת כרגע.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # תיבת הפרוטוקול המקצועית
    st.markdown("""
    <div class="check-list-container">
        <h4 style="color: #1565C0; margin-top: 0;">🔍 פרוטוקול בדיקות AI Elite</h4>
        <div style="font-size: 0.9rem; color: #555;">
            <p>✅ <b>ניתוח תנועה:</b> סריקה לאיתור צליעה, קושי בקימה או חוסר איזון בהליכה.</p>
            <p>✅ <b>משמעת בית:</b> זיהוי עלייה על ספה, נביחות אובססיביות או צרכים בבית.</p>
            <p>✅ <b>מעקב תזונה:</b> בדיקת זמינות מים/אוכל בקערות וזיהוי הרגלי אכילה.</p>
            <p>✅ <b>מניעת רעש:</b> התעלמות אוטומטית מבני אדם בחדר למניעת התראות שווא.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- מנוע הניטור ---
if st.session_state.cam_on:
    cap = cv2.VideoCapture(0)
    last_check_time = 0
    try:
        while st.session_state.cam_on:
            ret, frame = cap.read()
            if not ret: break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            video_spot.image(frame_rgb, width=780)

            now = time.time()
            if now - last_check_time > 60:
                last_check_time = now
                try:
                    _, buffer = cv2.imencode('.jpg', frame)
                    img_b64 = base64.b64encode(buffer).decode('utf-8')
                    
                    prompt = """Elite Dog Health Monitor:
                    1. Presence: If no dog (even if human is there), respond: STATUS: SAFE, REASON: תקין.
                    2. If dog is present, analyze: Gait/Limping, Sofa, Barking, Bowels status.
                    Format strictly: STATUS: [ALERT/SAFE/HEALTH], REASON: [Short Hebrew explanation ONLY if NOT SAFE]"""
                    
                    payload = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
                    res = requests.post(URL, json=payload, headers={'Content-Type': 'application/json'}).json()
                    
                    if 'candidates' in res:
                        full_text = res['candidates'][0]['content']['parts'][0]['text']
                        t_str = datetime.now().strftime("%H:%M:%S")
                        is_health = "HEALTH" in full_text.upper()
                        is_alert = "ALERT" in full_text.upper()
                        
                        if is_health or is_alert:
                            status_label = "🩺 בריאותי" if is_health else "🚨 חריגה"
                            final_reason = full_text.split("REASON:")[1].strip() if "REASON:" in full_text else "חריגה"
                            if is_health: st.session_state.health_alerts += 1
                            else: st.session_state.alerts_count += 1
                            
                            st.session_state.visual_history.append(cv2.resize(frame_rgb, (300, 200)))
                            send_email_alert(final_reason, t_str, status_label)
                        else:
                            status_label = "✅ תקין"
                            final_reason = "תקין"

                        st.session_state.history.insert(0, {"זמן": t_str, "מצב": status_label, "פירוט": final_reason})
                        log_spot.table(pd.DataFrame(st.session_state.history).head(10))
                        with gallery_spot.container():
                            cols = st.columns(2)
                            for i, img in enumerate(st.session_state.visual_history[-2:]):
                                cols[i].image(img)
                except: pass
            time.sleep(0.01)
    finally:
        cap.release()