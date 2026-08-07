# Frontend/app.py
import streamlit as st
import cv2
import numpy as np
import sys
from pathlib import Path
from typing import Dict, List
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av

# ----------------------------------------------------------
# PATH SETUP (critical)
# ----------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from Backend.live_recognition import process_frame, recognize_frame, draw_results
from Backend.database import search_best_matches, get_student, total_students
from live_camera import FaceRecognitionProcessor   # same folder

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Illegal As Fuck | Student Recognition",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# SESSION STATE
# ==========================================================
if "history" not in st.session_state:
    st.session_state.history = []

# ==========================================================
# CUSTOM CSS
# ==========================================================
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #0f172a;
    color: #e2e8f0;
}
.main { background-color: #0f172a; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
h1, h2, h3, h4 { color: #f8fafc !important; }
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2563eb, #1e40af);
}
.big-title {
    font-size: 2.6rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.subtitle {
    text-align: center;
    color: #94a3b8;
    font-size: 1.05rem;
    margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# HEADER
# ==========================================================
st.markdown('<div class="big-title">🎓 Illegal As Fuck</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Face Recognition • Smart Search • Live Camera</div>',
    unsafe_allow_html=True,
)
st.divider()

# ==========================================================
# SIDEBAR
# ==========================================================
with st.sidebar:
    st.title("🎓 System")
    st.metric("Total Students", total_students())
    st.metric("Engine", "InsightFace")
    st.metric("Mode", "Local + Live")
    st.divider()

    st.subheader("Recent Activity")
    if not st.session_state.history:
        st.info("No activity yet.")
    else:
        for item in st.session_state.history[:12]:
            if item["type"] == "Recognition":
                st.markdown(
                    f"**👤 {item['name']}**  \n"
                    f"Roll: `{item['roll']}`  \n"
                    f"Conf: {item['confidence']*100:.1f}%"
                )
            elif item["type"] == "Search":
                st.markdown(
                    f"**🔍 {item['name']}**  \n"
                    f"Roll: `{item['roll']}`  \n"
                    f"Score: {item['score']}"
                )
            else:
                st.markdown(
                    f"**📹 Live**  \n"
                    f"{item.get('name', 'Unknown')}"
                )
            st.caption("---")

# ==========================================================
# TABS
# ==========================================================
tab_search, tab_upload, tab_live = st.tabs(
    ["🔍 Smart Search", "📷 Upload / Camera", "📹 Live Camera"]
)

# ==========================================================
# TAB 1 – SMART SEARCH
# ==========================================================
with tab_search:
    st.subheader("Weighted Student Search")

    col1, col2, col3 = st.columns(3)
    with col1:
        roll = st.text_input("Roll Number", key="s_roll")
        name = st.text_input("Student Name", key="s_name")
    with col2:
        course = st.text_input("Course", key="s_course")
        semester = st.text_input("Semester", key="s_sem")
    with col3:
        stream = st.text_input("Stream", key="s_stream")
        section = st.text_input("Section", key="s_sec")

    if st.button("Search Students", use_container_width=True, type="primary"):
        filters = {
            "roll": roll,
            "name": name,
            "course": course,
            "semester": semester,
            "stream": stream,
            "section": section,
        }

        with st.spinner("Searching..."):
            matches = search_best_matches(filters, limit=25)

        if not matches:
            st.warning("No students found matching the criteria.")
        else:
            st.success(f"Found {len(matches)} matching student(s)")

            for student in matches:
                score = student["score"]
                if score >= 180:
                    badge = "🟢 Excellent"
                elif score >= 120:
                    badge = "🟡 Good"
                else:
                    badge = "🟠 Possible"

                with st.container(border=True):
                    c1, c2 = st.columns([1, 2.5])
                    with c1:
                        if student.get("photo"):
                            st.image(student["photo"], width=140)
                        else:
                            st.info("No photo")
                    with c2:
                        st.markdown(f"### {student['name']}")
                        st.write(f"**Roll:** {student['roll']}")
                        st.write(f"**Course:** {student['course']} | **Sem:** {student['semester']}")
                        st.write(f"**Stream:** {student['stream']} | **Sec:** {student['section']}")
                        st.metric("Search Score", score)
                        st.caption(badge)

                st.session_state.history.insert(0, {
                    "type": "Search",
                    "name": student["name"],
                    "roll": student["roll"],
                    "score": score,
                })

            st.session_state.history = st.session_state.history[:20]

# ==========================================================
# TAB 2 – UPLOAD / SINGLE PHOTO
# ==========================================================
with tab_upload:
    st.subheader("Recognize from Image")

    uploaded = st.file_uploader("Upload student photo", type=["jpg", "jpeg", "png"])
    camera = st.camera_input("Or take a photo")

    image_bytes = None
    if uploaded:
        image_bytes = uploaded.getvalue()
        st.image(uploaded, use_container_width=True)
    elif camera:
        image_bytes = camera.getvalue()
        st.image(camera, use_container_width=True)

    if st.button("Recognize Student", use_container_width=True, type="primary"):
        if image_bytes is None:
            st.warning("Please upload or capture an image first.")
        else:
            with st.spinner("Recognizing..."):
                nparr = np.frombuffer(image_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if img is None:
                    st.error("Could not decode image.")
                else:
                    results = recognize_frame(img)

                    if not results:
                        st.error("No face detected.")
                    else:
                        best = max(results, key=lambda r: r["confidence"])

                        if not best["matched"]:
                            st.error(f"Unknown person (confidence: {best['confidence']*100:.1f}%)")
                        else:
                            st.success("Student Recognized")
                            c1, c2 = st.columns([1, 2])
                            with c1:
                                if best.get("photo"):
                                    st.image(best["photo"], width=200)
                            with c2:
                                st.markdown(f"## {best['name']}")
                                st.write(f"**Roll:** {best['roll']}")
                                st.write(f"**Course:** {best['course']}")
                                st.write(f"**Semester:** {best['semester']}")
                                st.write(f"**Stream:** {best['stream']}")
                                st.write(f"**Section:** {best['section']}")

                            conf = best["confidence"]
                            st.progress(min(conf, 1.0))
                            st.metric("Confidence", f"{conf*100:.2f}%")

                            if conf >= 0.90:
                                st.success("Very High Confidence")
                            elif conf >= 0.75:
                                st.info("High Confidence")
                            elif conf >= 0.60:
                                st.warning("Moderate Confidence")
                            else:
                                st.error("Low Confidence")

                            st.session_state.history.insert(0, {
                                "type": "Recognition",
                                "name": best["name"],
                                "roll": best["roll"],
                                "confidence": conf,
                            })
                            st.session_state.history = st.session_state.history[:20]

# ==========================================================
# TAB 3 – LIVE CAMERA
# ==========================================================
with tab_live:
    st.subheader("Live Face Recognition")
    st.caption("Uses your webcam in real time. Green = known student, Red = unknown.")

    rtc_config = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )

    ctx = webrtc_streamer(
        key="live-recognition",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=rtc_config,
        video_processor_factory=FaceRecognitionProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

    if ctx.video_processor:
        results = ctx.video_processor.latest_results

        if results:
            st.markdown("### Current Detections")
            for r in results:
                if r["matched"]:
                    st.success(
                        f"**{r['name']}** | {r['stream']} | "
                        f"Conf: {r['confidence']*100:.1f}%"
                    )
                    if r["confidence"] > 0.70:
                        st.session_state.history.insert(0, {
                            "type": "Live",
                            "name": r["name"],
                            "roll": r.get("roll", ""),
                            "confidence": r["confidence"],
                        })
                        st.session_state.history = st.session_state.history[:20]
                else:
                    st.error(f"Unknown | Conf: {r['confidence']*100:.1f}%")
        else:
            st.info("Point the camera at a face…")

# ==========================================================
# FOOTER
# ==========================================================
st.divider()
st.caption("Frontend: Streamlit + streamlit-webrtc  |  Backend: InsightFace + process_frame()")