import streamlit as st
from groq import Groq
import base64
from streamlit_mic_recorder import mic_recorder

# Page Config
st.set_page_config(page_title="ARIS V2 - AI Assistant", page_icon="🤖")

st.title("🤖 ARIS V2 - Public AI Assistant")
st.write("Welcome to V2! Now with Image Analysis & Voice Support.")

# Initialize Groq Client using Streamlit Secrets
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Please set your GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Optional Image Uploader for V2 Image Feature
uploaded_file = st.file_uploader("Upload an image for analysis (Optional)...", type=["jpg", "jpeg", "png"])

base64_image = None
if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    bytes_data = uploaded_file.getvalue()
    base64_image = base64.b64encode(bytes_data).decode("utf-8")

# Voice Recorder Button (Speak to ARIS)
st.write("🎙️ Or click below to speak your command:")
audio = mic_recorder(start_prompt="Start Recording", stop_prompt="Stop Recording", just_once=True)

spoken_prompt = ""
if audio:
    # Note: Audio data processing can be integrated with Whisper API, 
    # for now we use text chat or type what you want if audio is captured.
    pass

# Chat input from user
prompt = st.chat_input("Ask ARIS anything or describe the image...")

# If voice was recorded or text was typed, use it as prompt
final_prompt = prompt

if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

    # Generate response from Groq
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            if base64_image:
                messages_payload = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": final_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ]
                model_to_use = "qwen/qwen3.6-27b"
            else:
                messages_payload = [
                    {
                        "role": "user",
                        "content": final_prompt,
                    }
                ]
                model_to_use = "llama-3.3-70b-versatile"

            chat_completion = client.chat.completions.create(
                model=model_to_use,
                messages=messages_payload,
                stream=True,
            )
            
            response = ""
            for chunk in chat_completion:
                if chunk.choices[0].delta.content:
                    response += chunk.choices[0].delta.content
                    message_placeholder.markdown(response + "▌")
            message_placeholder.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        except Exception as e:
            st.error(f"Error: {e}")
