import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import cv2
import requests
import base64
import pandas as pd
import time
from datetime import datetime

# --- הגדרות ליבה ---
API_KEY = "AIzaSyCViOTuoBmPtAcRTT_8zmmQYT-Z4pn6C3U"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

st.set_page_config(page_title="Lindo Guard Light", layout="wide")

# שימוש בזיכרון מטמון כדי למנוע קריסות
if 'history' not in st.session_state: st.session_state.history = []
if 'last_check' not in st.session_state: st.session_state.last_check = 0

st.title("🛡️ Lindo Guard - Mobile Optimized")

# הגדרות חיבור בסיסיות ויציבות
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

col_left, col_right = st.columns([2, 1])

with col_right:
    st.write("📜 יומן אירועים")
    if st.session_state.history:
        st.table(pd.DataFrame(st.session_state.history).head(5))

with col_left:
    # מצלמה בגרסה קלה שלא תוקעת את הטלפון
    ctx = webrtc_streamer(
        key="lindo-light",
        rtc_configuration=RTC_CONFIG,
        media_stream_constraints={"video": True, "audio": False},
        video_html_attrs={"style": {"width": "100%", "margin": "0 auto", "border": "2px solid #1565C0", "border-radius": "10px"}},
    )

    # לוגיקת ניתוח חיצונית למניעת עומס זיכרון
    if ctx.video_receiver:
        try:
            frame = ctx.video_receiver.get_frame(timeout=1)
            if frame:
                img = frame.to_ndarray(format="bgr24")
                now = time.time()
                
                # ניתוח פעם בדקה כדי לשמור על המשאבים של Streamlit
                if now - st.session_state.last_check > 60:
                    st.session_state.last_check = now
                    small = cv2.resize(img, (160, 120))
                    _, buff = cv2.imencode('.jpg', small)
                    b64 = base64.b64encode(buff).decode('utf-8')
                    
                    payload = {"contents": [{"parts": [{"text": "Analyze dog: Status (OK/ALERT/HEALTH) + 1 sentence Hebrew."}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
                    r = requests.post(URL, json=payload, timeout=5).json()
                    ans = r['candidates'][0]['content']['parts'][0]['text']
                    
                    st.session_state.history.insert(0, {"זמן": datetime.now().strftime("%H:%M"), "מצב": ans})
                    st.rerun() # מרענן את הטבלה
        except:
            pass
