# Frontend/app.py
import streamlit as st
from api import recognize, search_students, get_total_students

st.set_page_config(
    page_title="Illegal As Fuck | Student Recognition",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "history" not in st.session_state:
    st.session_state.history = []

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

st.markdown('<div class="big-title">🎓 Illegal As Fuck</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Face Recognition • Smart Search</div>',
    unsafe_allow_html=True,
)
st.divider()

# ==========================================================
# SIDEBAR
# ==========================================================
with st.sidebar:
    st.title("🎓 System")

    try:
        total = get_total_students()
        st.success("✅ Backend Online")
        st.caption("Connected via Cloudflare Tunnel")
    except Exception:
        total = 0
        st.error("❌ Backend Offline")
        st.caption("Check your laptop + Cloudflare tunnel")

    st.metric("Total Students", total if total else "—")
    st.metric("Engine", "InsightFace")
    st.metric("Mode", "Cloudflare Tunnel")
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
            st.caption("---")

# ==========================================================
# TABS
# ==========================================================
tab_search, tab_upload = st.tabs(
    ["🔍 Smart Search", "📷 Upload / Camera"]
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
            try:
                matches = search_students(filters)
            except Exception as e:
                st.error(f"Backend error: {e}")
                matches = []

        # Normalize response
        if isinstance(matches, dict):
            matches = matches.get("results", matches.get("data", matches.get("students", [])))

        if not isinstance(matches, list):
            st.error("Unexpected response from Backend")
            matches = []

        if not matches:
            st.warning("No students found matching the criteria.")
        else:
            st.success(f"Found {len(matches)} matching student(s)")

            for student in matches:
                if not isinstance(student, dict):
                    st.write(student)
                    continue

                score = student.get("score", 0)
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
                        st.markdown(f"### {student.get('name', 'Unknown')}")
                        st.write(f"**Roll:** {student.get('roll', '')}")
                        st.write(f"**Course:** {student.get('course', '')} | **Sem:** {student.get('semester', '')}")
                        st.write(f"**Stream:** {student.get('stream', '')} | **Sec:** {student.get('section', '')}")
                        st.metric("Search Score", score)
                        st.caption(badge)

                st.session_state.history.insert(0, {
                    "type": "Search",
                    "name": student.get("name", ""),
                    "roll": student.get("roll", ""),
                    "score": score,
                })

            st.session_state.history = st.session_state.history[:20]

# ==========================================================
# TAB 2 – UPLOAD / CAMERA
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
            with st.spinner("Recognizing via Backend..."):
                try:
                    result = recognize(image_bytes)

                    if isinstance(result, list):
                        results = result
                    elif isinstance(result, dict):
                        results = result.get("results", result.get("data", [result]))
                    else:
                        results = []

                    if not results:
                        st.error("No face detected.")
                    else:
                        best = max(results, key=lambda r: r.get("confidence", 0) if isinstance(r, dict) else 0)

                        if not isinstance(best, dict) or not best.get("matched", False):
                            conf = best.get("confidence", 0) if isinstance(best, dict) else 0
                            st.error(f"Unknown person (confidence: {conf*100:.1f}%)")
                        else:
                            st.success("Student Recognized")
                            c1, c2 = st.columns([1, 2])
                            with c1:
                                if best.get("photo"):
                                    st.image(best["photo"], width=200)
                            with c2:
                                st.markdown(f"## {best.get('name', '')}")
                                st.write(f"**Roll:** {best.get('roll', '')}")
                                st.write(f"**Course:** {best.get('course', '')}")
                                st.write(f"**Semester:** {best.get('semester', '')}")
                                st.write(f"**Stream:** {best.get('stream', '')}")
                                st.write(f"**Section:** {best.get('section', '')}")

                            conf = best.get("confidence", 0)
                            st.progress(min(float(conf), 1.0))
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
                                "name": best.get("name", ""),
                                "roll": best.get("roll", ""),
                                "confidence": conf,
                            })
                            st.session_state.history = st.session_state.history[:20]

                except Exception as e:
                    st.error(f"Backend error: {e}")

st.divider()
st.caption("Frontend: Streamlit Cloud  |  Backend: Your Laptop via Cloudflare Tunnel")