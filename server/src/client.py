# https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps
import streamlit as st
import requests
import base64

# FUNCTIONS 
    
# Use server service name when running in Docker, localhost for local development
# BASE_API_URL = "http://server:8000/api/v1"
BASE_API_URL = "http://localhost:8000/api/v1"
CHAT_PDF = "Chat PDF"
RESEARCH = "Research"



def get_info():
    url = f"{BASE_API_URL}/info"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("code") != 200:
            return f"Error: {data.get('message', 'Unknown error occurred.')}"
        return data.get("data", {})
    except Exception as e:
        return f"Error: {e}"


def send_message(message):
    if st.session_state.active_mode == CHAT_PDF:
        url = f"{BASE_API_URL}/chat_docs"
    else:
        url = f"{BASE_API_URL}/research"

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

def update_model_api(model_name):
    url = f"{BASE_API_URL}/update_model"
    try:
        response = requests.post(url, json={"model_name": model_name})
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") != 200:
            return False, f"Error: {data.get('message', 'Unknown error occurred.')}"
        return True, data.get("message", "Model updated successfully.")
    except Exception as e:
        return False, f"Error: {e}"
    
# UI SETUP

# INITIALIZE SESSION STATE
modes = [CHAT_PDF, RESEARCH]

if "active_mode" not in st.session_state:
    st.session_state.active_mode = RESEARCH

if "messages" not in st.session_state:
    st.session_state.messages = []

if "file_names" not in st.session_state:
    st.session_state.file_names = []

info = get_info()

if "settings" not in st.session_state:
    st.session_state.settings = {
        "model": info.get("models", {}).get("active_model")
    }
model_selected = st.session_state.settings.get("model")


#----- HEADER -----
st.set_page_config(
    page_title="Africa Insights Navigator", 
    page_icon="✨",
    layout="wide"
)

st.title("Africa Insights Navigator")

# ----- SIDEBAR -----
@st.dialog("Settings")
def settings_dialog():
    st.subheader("Adjust your settings below:")

    available_models = info.get("models", {}).get("available_models", [])
    current_model = st.session_state.settings.get("model")
    
    # Store the selected model in a variable
    model_selected = st.selectbox(
        "Select a model",
        available_models,
        index=available_models.index(current_model) if current_model in available_models else 0
    )
    
    # Only call the API if the model has changed
    if model_selected != current_model:
        success, message = update_model_api(model_selected)
        
        if success:
            st.session_state.settings.update({"model": model_selected})
            st.success(message)
        else:
            st.error(message)

with st.sidebar:
    st.subheader("Settings")
    if st.button("Settings"):
        settings_dialog()

    st.write("--------------------")
    st.subheader("Mode")

    active_mode = st.segmented_control(
        "Select research mode", modes, selection_mode="single", default=RESEARCH
    )
    # Update session state when mode changes
    if st.session_state.active_mode != active_mode:
        st.session_state.active_mode = active_mode
    
    st.write("---------------------")
    if st.session_state.active_mode == CHAT_PDF:
        st.subheader("Uploaded Documents")
        if st.session_state.file_names:
            for name in st.session_state.file_names:
                st.write(f"- {name}")
        else:
            st.write("No documents uploaded yet.")
        uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

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
                        if uploaded_file.name not in st.session_state.file_names:
                            st.session_state.file_names.append(uploaded_file.name)
                    else:
                        st.error(message)

# ----- CHAT -----
with st.chat_message("assistant"):
    st.write("How can I help you with your research today?")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

should_disable_chat = len(st.session_state.file_names) == 0 and active_mode == CHAT_PDF
user_input = st.chat_input("Type your message here...", disabled=should_disable_chat)
if should_disable_chat:
    st.info("Please upload a PDF document to chat about it.")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.markdown(send_message(user_input))
    
    st.session_state.messages.append({"role": "assistant", "content": response})

