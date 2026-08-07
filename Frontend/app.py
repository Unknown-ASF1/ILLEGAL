import streamlit as st
from PIL import Image
import requests
import io

if "history" not in st.session_state:
    st.session_state.history = []

# ==============================
# CONFIG
# ==============================

API_URL = "https://superintendent-requirements-radar-focused.trycloudflare.com"

st.set_page_config(
    page_title="Illegas AS Fuck",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================
# CSS
# ==============================

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

.title{
    text-align:center;
    font-size:42px;
    font-weight:bold;
    color:white;
}

.subtitle{
    text-align:center;
    color:#94a3b8;
    margin-bottom:30px;
}

.card{
    background:#1e293b;
    border-radius:18px;
    padding:25px;
    box-shadow:0px 8px 20px rgba(0,0,0,0.4);
}

.small{
    color:#94a3b8;
}

.metric{
    font-size:28px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# TITLE
# ==============================

st.markdown(
    "<div class='title'>🎓 Illegas AS Fuck</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitle'>Illegal As Fuck</div>",
    unsafe_allow_html=True
)

# ==============================
# LAYOUT
# ==============================

left, right = st.columns([1.3,1])

with left:

    st.markdown("### 📷 Scan Student")

    uploaded = st.file_uploader(
        "Upload Image",
        type=["jpg","jpeg","png"]
    )

    camera = st.camera_input("Or Take Picture")

    image = None

    if uploaded:

        image = uploaded

        st.image(uploaded,use_container_width=True)

    elif camera:

        image = camera

        st.image(camera,use_container_width=True)

    recognize = st.button(
        "🔍 Recognize Student",
        use_container_width=True
    )

with right:

    st.markdown("### 👤 Student Details")

    placeholder = st.empty()

# ==============================
# API
# ==============================

if recognize and image:

    with st.spinner("Recognizing..."):

        files = {
            "file": image.getvalue()
        }

        response = requests.post(
            API_URL + "/recognize",
            files=files
        )

        data = response.json()

    if data["matched"]:

        student = data["student"]

        with placeholder.container():

            st.success("Student Found")

            st.image(
                student["photo"],
                width=180
            )

            st.markdown(f"## {student['name']}")

            st.write(f"**Roll No:** {student['roll']}")

            st.write(f"**Course:** {student['course']}")

            st.write(f"**Semester:** {student['semester']}")

            st.write(f"**Stream:** {student['stream']}")

            st.write(f"**Section:** {student['section']}")

            st.progress(
                min(
                    data["confidence"],
                    1.0
                )
            )

            st.write(
                f"Confidence : {round(data['confidence']*100,2)}%"
            )

    else:

        with placeholder.container():

            st.error("Student Not Found")

    with st.sidebar:

        st.title("Illegal As Fuck")

        st.success("Backend Connected")

        st.metric("Students Indexed", "4508")

        st.metric("Recognition Model", "InsightFace")

        st.metric("Status", "Online")