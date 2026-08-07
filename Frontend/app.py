import streamlit as st
import requests
from PIL import Image
import io

# ==========================================================
# CONFIG
# ==========================================================

st.set_page_config(
    page_title="Student Recognition System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://127.0.0.1:8000"

if "history" not in st.session_state:
    st.session_state.history = []

# ==========================================================
# CUSTOM CSS
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
    padding-bottom:2rem;
}

h1,h2,h3,h4{
    color:white;
}

.card{
    background:#1e293b;
    padding:20px;
    border-radius:18px;
    border:1px solid #334155;
}

.result-card{
    background:#1e293b;
    padding:25px;
    border-radius:18px;
    border:1px solid #334155;
}

.metric-box{
    background:#1e293b;
    padding:15px;
    border-radius:12px;
    text-align:center;
}

footer{
    visibility:hidden;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# HEADER
# ==========================================================

st.title("🎓 Student Recognition System")
st.caption("Face Recognition + Student Database Search")

st.divider()

# ==========================================================
# LAYOUT
# ==========================================================

search_col, recognize_col, result_col = st.columns(
    [1.2, 1.2, 1.4]
)

# ==========================================================
# SEARCH PANEL
# ==========================================================

with search_col:

    st.subheader("🔍 Search Student")

    search_field = st.selectbox(
        "Search By",
        [
            "Roll No",
            "Name",
            "Course",
            "Semester",
            "Stream",
            "Section"
        ]
    )

    search_value = st.text_input(
        "Enter Value"
    )

    search_button = st.button(
        "Search Database",
        use_container_width=True
    )

# ==========================================================
# FACE RECOGNITION PANEL
# ==========================================================

with recognize_col:

    st.subheader("📷 Face Recognition")

    uploaded_image = st.file_uploader(
        "Upload Student Image",
        type=["jpg", "jpeg", "png"]
    )

    captured_image = st.camera_input(
        "Or Capture Image"
    )

    image_file = None

    if uploaded_image is not None:
        image_file = uploaded_image
        st.image(uploaded_image, use_container_width=True)

    elif captured_image is not None:
        image_file = captured_image
        st.image(captured_image, use_container_width=True)

    recognize_button = st.button(
        "Recognize Student",
        use_container_width=True
    )

# ==========================================================
# RESULT PANEL
# ==========================================================

with result_col:

    st.subheader("👤 Result")

    result_placeholder = st.empty()


# ==========================================================
# SEARCH API
# ==========================================================

if search_button:

    if search_value.strip() == "":

        with result_placeholder.container():
            st.warning("Please enter a value to search.")

    else:

        payload = {
            "field": search_field,
            "value": search_value
        }

        try:

            response = requests.post(
                f"{API_URL}/search",
                json=payload,
                timeout=30
            )

            data = response.json()

            with result_placeholder.container():

                if not data.get("found"):

                    st.error(
                        data.get(
                            "message",
                            "No student found."
                        )
                    )

                else:

                    # --------------------------------------
                    # Roll Number returns single student
                    # --------------------------------------

                    if search_field == "Roll No":

                        student = data["student"]

                        st.success("Student Found")

                        st.image(
                            student["photo"],
                            width=180
                        )

                        st.markdown(
                            f"## {student['name']}"
                        )

                        st.write(
                            f"**Roll No:** {student['roll']}"
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

                        st.session_state.history.insert(
                            0,
                            {
                                "type": "Search",
                                "name": student["name"],
                                "roll": student["roll"]
                            }
                        )

                    # --------------------------------------
                    # Other fields return multiple students
                    # --------------------------------------

                    else:

                        st.success(
                            f"{data['count']} student(s) found."
                        )

                        for student in data["students"]:

                            with st.container(border=True):

                                c1, c2 = st.columns(
                                    [1, 3]
                                )

                                with c1:

                                    st.image(
                                        student["photo"],
                                        width=100
                                    )

                                with c2:

                                    st.markdown(
                                        f"### {student['name']}"
                                    )

                                    st.write(
                                        f"**Roll:** {student['roll']}"
                                    )

                                    st.write(
                                        f"**Course:** {student['course']}"
                                    )

                                    st.write(
                                        f"Semester: {student['semester']}"
                                    )

                                    st.write(
                                        f"Stream: {student['stream']}"
                                    )

                                    st.write(
                                        f"Section: {student['section']}"
                                    )

        except Exception as e:

            with result_placeholder.container():

                st.error(
                    f"Unable to connect to backend.\n\n{e}"
                )

# ==========================================================
# FACE RECOGNITION API
# ==========================================================

if recognize_button:

    if image_file is None:

        with result_placeholder.container():
            st.warning("Please upload or capture an image.")

    else:

        try:

            with st.spinner("Recognizing student..."):

                files = {
                    "file": (
                        "student.jpg",
                        image_file.getvalue(),
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

                if not data.get("matched"):

                    st.error(
                        data.get(
                            "message",
                            "Student not found."
                        )
                    )

                else:

                    student = data["student"]

                    confidence = data["confidence"]

                    st.success("Student Recognized")

                    st.image(
                        student["photo"],
                        width=220
                    )

                    st.markdown(
                        f"## {student['name']}"
                    )

                    st.write(
                        f"**Roll No:** {student['roll']}"
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

                    st.progress(
                        min(confidence, 1.0)
                    )

                    st.write(
                        f"Recognition Confidence: {confidence * 100:.2f}%"
                    )

                    st.session_state.history.insert(
                        0,
                        {
                            "type": "Recognition",
                            "name": student["name"],
                            "roll": student["roll"],
                            "confidence": confidence
                        }
                    )

        except Exception as e:

            with result_placeholder.container():

                st.error(
                    f"Recognition failed.\n\n{e}"
                )

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title("🎓 Student Recognition")

    st.success("Backend Connected")

    st.divider()

    st.subheader("System Status")

    st.metric(
        "Recognition Engine",
        "InsightFace"
    )

    st.metric(
        "API Status",
        "Online"
    )

    st.metric(
        "Search Mode",
        "Database"
    )

    st.divider()

    st.subheader("Recent Activity")

    if len(st.session_state.history) == 0:

        st.info("No activity yet.")

    else:

        for item in st.session_state.history[:10]:

            if item["type"] == "Recognition":

                st.markdown(
                    f"""
**🟢 Recognition**

**{item['name']}**

Roll No: {item['roll']}

Confidence: {item['confidence'] * 100:.2f}%
"""
                )

            else:

                st.markdown(
                    f"""
**🔍 Search**

**{item['name']}**

Roll No: {item['roll']}
"""
                )

            st.divider()

# ==========================================================
# FOOTER
# ==========================================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.caption("Frontend: Streamlit")

with col2:
    st.caption("Backend: FastAPI")

with col3:
    st.caption("Recognition: InsightFace")