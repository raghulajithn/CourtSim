import streamlit as st
import requests
import uuid

# Set the FastAPI backend URL
API_URL = "http://localhost:8001"

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("⚖️ Courtroom Simulator")

# File Upload Section
st.header("📁 Upload Case Files")
with st.form("upload_form"):
    opposition_file = st.file_uploader(
        "Upload Opposition Document (PDF)", type="pdf", key="opposition"
    )
    laws_file = st.file_uploader("Upload Laws Document (PDF)", type="pdf", key="laws")
    submit_upload = st.form_submit_button("Upload Files")

if submit_upload:
    if opposition_file and laws_file:
        files = {
            "opposition": (opposition_file.name, opposition_file, "application/pdf"),
            "laws": (laws_file.name, laws_file, "application/pdf"),
        }
        response = requests.post(f"{API_URL}/upload/", files=files)
        if response.status_code == 200:
            st.success("Files uploaded and processed successfully.")
        else:
            st.error("Failed to upload files.")
    else:
        st.warning("Please upload both opposition and laws documents.")

# Chat Interface
st.header("🗣️ Trial Proceedings")
user_input = st.text_input("Your Message:", key="user_input")
if st.button("Send"):
    if user_input:
        payload = {"session_id": st.session_state.session_id, "user_msg": user_input}
        response = requests.post(f"{API_URL}/trial/", json=payload)
        if response.status_code == 200:
            opponent_reply = response.json().get("reply", "")
            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("Opponent", opponent_reply))
        else:
            st.error("Failed to get a response from the opponent.")

# Display Chat History
for speaker, message in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {message}")

# Verdict Section
st.header("🧑‍⚖️ Judge's Verdict")
if st.button("Get Verdict"):
    if st.session_state.chat_history:
        history_text = "\n".join(
            [
                f"{speaker}: {message}"
                for speaker, message in st.session_state.chat_history
            ]
        )
        payload = {"session_id": st.session_state.session_id, "history": history_text}
        response = requests.post(f"{API_URL}/verdict/", json=payload)
        if response.status_code == 200:
            verdict = response.json().get("verdict", "")
            st.subheader("Verdict:")
            st.write(verdict)
        else:
            st.error("Failed to retrieve the verdict.")
    else:
        st.warning(
            "No conversation history found. Engage in a trial before requesting a verdict."
        )
