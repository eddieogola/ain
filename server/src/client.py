# https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps
import streamlit as st
import requests
import base64


# FUNCTIONS

BASE_API_URL = "http://server:8000/api/v1"


def send_message(message):
    # Use server service name when running in Docker, localhost for local development
    url = f"{BASE_API_URL}/chat-docs"
    try:
        response = requests.post(url, json={"message": message})
        response.raise_for_status()
        data = response.json()
        message = data.get("message", "")

        if data.get("code") != 200:
            return f"Error: {message or 'Unknown error occurred.'}"
        return data.get("data", {}).get("message", "No report found.")
    except Exception as e:
        return f"Error: {e}"

def upload_pdf_to_api(file_bytes, filename):
    url = f"{BASE_API_URL}/doc-index"
    
    try:
        # Encode the file as base64
        encoded_file = base64.b64encode(file_bytes).decode('utf-8')
        
        # Send the file to the API
        response = requests.post(
            url, 
            json={
                "filename": filename,
                "file_data": encoded_file
            }
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") != 200:
            return False, f"Error: {data.get('message', 'Unknown error occurred.')}"
        return True, data.get("data", {}).get("message", "Document uploaded successfully.")
    except Exception as e:
        return False, f"Error: {e}"


# UI SETUP
st.set_page_config(
    page_title="Africa Insights Navigator", 
    page_icon="✨",
    layout="wide"
)
st.title("Africa Insights Navigator")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.chat_message("assistant"):
    st.write("How can I help you with your research today?")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.markdown(send_message(user_input))
    
    st.session_state.messages.append({"role": "assistant", "content": response})

# Model Selection
st.subheader("Model Selection")
option = st.selectbox(
    "Select a model",
    ("Gemini 2.5 Flash", ""),
)

st.write("You selected:", option)

# PDF Upload section
st.subheader("Upload Research Document")
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    # Show file details
    file_details = {
        "Filename": uploaded_file.name,
        "File size": f"{uploaded_file.size / 1024:.2f} KB"
    }
    st.write("File Name:", file_details["Filename"])
    st.write("File Size:", file_details["File size"])
    
    # Add a button to confirm upload
    if st.button("Upload Document"):
        with st.spinner("Uploading document..."):
            # Get file bytes
            file_bytes = uploaded_file.getvalue()
            
            # Send to API
            success, message = upload_pdf_to_api(file_bytes, uploaded_file.name)
            
            if success:
                st.success(message)
            else:
                st.error(message)