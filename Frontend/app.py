import streamlit as st

st.set_page_config(page_title="Test", layout="wide")

st.title("🎓 Illegal As Fuck - Debug Mode")
st.write("If you can see this, the basic Streamlit app is working.")

st.info("Now checking API connection...")

try:
    from api import API_URL
    st.write(f"API_URL = `{API_URL}`")
except Exception as e:
    st.error(f"Could not import api.py: {e}")

st.write("End of debug page.")