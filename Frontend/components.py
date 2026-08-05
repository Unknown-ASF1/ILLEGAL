import streamlit as st


def student_card(student):

    st.success("Student Found")

    col1, col2 = st.columns([1,2])

    with col1:
        st.image(student["photo"], width=180)

    with col2:
        st.markdown(f"### {student['name']}")
        st.write(f"**Roll No:** {student['roll']}")
        st.write(f"**Course:** {student['course']}")
        st.write(f"**Semester:** {student['semester']}")
        st.write(f"**Stream:** {student['stream']}")
        st.write(f"**Section:** {student['section']}")