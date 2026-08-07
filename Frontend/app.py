import streamlit as st
import requests

# ==========================================================
# CONFIG
# ==========================================================

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Student Recognition System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# SESSION STATE
# ==========================================================

if "history" not in st.session_state:
    st.session_state.history = []

# ==========================================================
# CSS
# ==========================================================

st.markdown("""
<style>

html, body, [class*="css"]{
    background:#0f172a;
    color:white;
}

.main{
    background:#0f172a;
}

.block-container{
    padding-top:2rem;
}

.card{
    background:#1e293b;
    border-radius:15px;
    padding:20px;
    border:1px solid #334155;
    margin-bottom:20px;
}

.result-card{
    background:#111827;
    border-radius:12px;
    padding:15px;
    margin-bottom:15px;
    border:1px solid #334155;
}

.small-text{
    color:#94a3b8;
    font-size:14px;
}

.big-title{
    font-size:42px;
    font-weight:bold;
    text-align:center;
    color:white;
}

.subtitle{
    text-align:center;
    color:#94a3b8;
    margin-bottom:30px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# TITLE
# ==========================================================

st.markdown(
    "<div class='big-title'>🎓 Student Recognition System</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitle'>Face Recognition + Smart Student Search</div>",
    unsafe_allow_html=True
)

st.divider()

# ==========================================================
# MAIN LAYOUT
# ==========================================================

left, middle, right = st.columns([1.2,1.2,1.6])

# ==========================================================
# SEARCH PANEL
# ==========================================================

with left:

    st.subheader("🔍 Smart Search")

    roll = st.text_input(
        "Roll Number"
    )

    name = st.text_input(
        "Student Name"
    )

    course = st.text_input(
        "Course"
    )

    semester = st.text_input(
        "Semester"
    )

    stream = st.text_input(
        "Stream"
    )

    section = st.text_input(
        "Section"
    )

    search_button = st.button(
        "Search Students",
        use_container_width=True
    )

# ==========================================================
# FACE RECOGNITION PANEL
# ==========================================================

with middle:

    st.subheader("📷 Face Recognition")

    uploaded = st.file_uploader(
        "Upload Student Image",
        type=["jpg","jpeg","png"]
    )

    camera = st.camera_input(
        "Take Photo"
    )

    image = None

    if uploaded:

        image = uploaded
        st.image(
            uploaded,
            use_container_width=True
        )

    elif camera:

        image = camera

        st.image(
            camera,
            use_container_width=True
        )

    recognize_button = st.button(
        "Recognize Student",
        use_container_width=True
    )

# ==========================================================
# RESULT PANEL
# ==========================================================

with right:

    st.subheader("📋 Results")

    result_placeholder = st.empty()


# ==========================================================
# SMART SEARCH
# ==========================================================

if search_button:

    payload = {
        "roll": roll,
        "name": name,
        "course": course,
        "semester": semester,
        "stream": stream,
        "section": section,
    }

    try:

        with st.spinner("Searching students..."):

            response = requests.post(
                f"{API_URL}/search",
                json=payload,
                timeout=30
            )

        data = response.json()

        with result_placeholder.container():

            if not data["found"]:

                st.error(
                    data.get(
                        "message",
                        "No students found."
                    )
                )

            else:

                st.success(
                    f"{data['count']} matching student(s) found"
                )

                for student in data["students"]:

                    score = student["score"]

                    if score >= 180:
                        color = "🟢"
                        label = "Excellent Match"

                    elif score >= 120:
                        color = "🟡"
                        label = "Good Match"

                    else:
                        color = "🟠"
                        label = "Possible Match"

                    with st.container(border=True):

                        c1, c2 = st.columns(
                            [1, 2]
                        )

                        with c1:

                            st.image(
                                student["photo"],
                                width=150
                            )

                        with c2:

                            st.markdown(
                                f"### {student['name']}"
                            )

                            st.write(
                                f"**Roll Number:** {student['roll']}"
                            )

                            st.write(
                                f"**Course:** {student['course']}"
                            )

                            st.write(
                                f"**Semester:** {student['semester']}"
                            )

                            st.write(
                                f"**Stream:** {student['stream']}"
                            )

                            st.write(
                                f"**Section:** {student['section']}"
                            )

                            st.metric(
                                "Search Score",
                                score
                            )

                            st.caption(
                                f"{color} {label}"
                            )

                    st.session_state.history.insert(
                        0,
                        {
                            "type": "Search",
                            "name": student["name"],
                            "roll": student["roll"],
                            "score": score,
                        }
                    )

        if len(st.session_state.history) > 20:

            st.session_state.history = (
                st.session_state.history[:20]
            )

    except Exception as e:

        with result_placeholder.container():

            st.error(
                f"Backend Error\n\n{e}"
            )

# ==========================================================
# FACE RECOGNITION
# ==========================================================

if recognize_button:

    if image is None:

        with result_placeholder.container():

            st.warning(
                "Please upload or capture an image."
            )

    else:

        try:

            with st.spinner("Recognizing Student..."):

                files = {
                    "file": (
                        "student.jpg",
                        image.getvalue(),
                        "image/jpeg"
                    )
                }

                response = requests.post(
                    f"{API_URL}/recognize",
                    files=files,
                    timeout=60
                )

                data = response.json()

            with result_placeholder.container():

                if not data["matched"]:

                    st.error(
                        data.get(
                            "message",
                            "Student Not Found"
                        )
                    )

                else:

                    student = data["student"]

                    confidence = data["confidence"]

                    st.success(
                        "Student Successfully Recognized"
                    )

                    top_left, top_right = st.columns(
                        [1, 2]
                    )

                    with top_left:

                        st.image(
                            student["photo"],
                            width=220
                        )

                    with top_right:

                        st.markdown(
                            f"## {student['name']}"
                        )

                        st.write(
                            f"**Roll Number:** {student['roll']}"
                        )

                        st.write(
                            f"**Course:** {student['course']}"
                        )

                        st.write(
                            f"**Semester:** {student['semester']}"
                        )

                        st.write(
                            f"**Stream:** {student['stream']}"
                        )

                        st.write(
                            f"**Section:** {student['section']}"
                        )

                    st.divider()

                    st.subheader(
                        "Recognition Confidence"
                    )

                    st.progress(
                        min(confidence, 1.0)
                    )

                    st.metric(
                        "Confidence",
                        f"{confidence*100:.2f}%"
                    )

                    if confidence >= 0.90:

                        st.success(
                            "Very High Confidence Match"
                        )

                    elif confidence >= 0.75:

                        st.info(
                            "High Confidence Match"
                        )

                    elif confidence >= 0.60:

                        st.warning(
                            "Moderate Confidence Match"
                        )

                    else:

                        st.error(
                            "Low Confidence Match"
                        )

                    st.session_state.history.insert(
                        0,
                        {
                            "type": "Recognition",
                            "name": student["name"],
                            "roll": student["roll"],
                            "confidence": confidence,
                        }
                    )

                    if len(st.session_state.history) > 20:

                        st.session_state.history = (
                            st.session_state.history[:20]
                        )

        except Exception as e:

            with result_placeholder.container():

                st.error(
                    f"Recognition Failed\n\n{e}"
                )


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title("🎓 Student Recognition")

    st.success("Backend Connected")

    st.divider()

    st.subheader("System")

    st.metric(
        "Recognition",
        "InsightFace"
    )

    st.metric(
        "Search",
        "Weighted Search"
    )

    st.metric(
        "API",
        "Online"
    )

    st.divider()

    st.subheader("Recent Activity")

    if len(st.session_state.history) == 0:

        st.info(
            "No activity yet."
        )

    else:

        for item in st.session_state.history:

            if item["type"] == "Recognition":

                st.markdown(
                    f"""
### 👤 {item['name']}

**Roll:** {item['roll']}

Recognition

Confidence:
{item['confidence']*100:.2f}%

---
"""
                )

            else:

                st.markdown(
                    f"""
### 🔍 {item['name']}

**Roll:** {item['roll']}

Search Score:
{item['score']}

---
"""
                )

# ==========================================================
# FOOTER
# ==========================================================

st.divider()

left, center, right = st.columns(3)

with left:

    st.caption(
        "Frontend : Streamlit"
    )

with center:

    st.caption(
        "Backend : FastAPI"
    )

with right:

    st.caption(
        "Recognition : InsightFace"
    )

st.markdown(
    """
<div style='text-align:center;
padding:15px;
color:#94a3b8;'>

Student Recognition System

Powered by InsightFace, FastAPI and Streamlit

</div>
""",
    unsafe_allow_html=True,
)