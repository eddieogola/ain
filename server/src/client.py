import streamlit as st
import requests

st.set_page_config(
    page_title="Africa Insights Navigator", 
    page_icon="✨",
    layout="wide"
)
st.title("Africa Insights Navigator")

if "messages" not in st.session_state:
    st.session_state.messages = []

def send_message(message):
    # Use server service name when running in Docker, localhost for local development
    base_url = "http://server:8000" 

    url = f"{base_url}/api/v1/research"
    try:
        response = requests.post(url, json={"message": message})
        response.raise_for_status()
        data = response.json()
        message = data.get("message", "")
        print(data)
        if data.get("code") != 200:
            return f"Error: {message or 'Unknown error occurred.'}"
        return data.get("data", {}).get("message", "No report found.")
    except Exception as e:
        return f"Error: {e}"

with st.chat_message("assistant"):
    st.write("How can I help you with your research today?")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = send_message(user_input)
        st.write(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
