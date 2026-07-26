import streamlit as st
from groq import Groq
import base64

# Page Config
st.set_page_config(page_title="ARIS V2 - AI Assistant", page_icon="🤖")

st.title("🤖 ARIS V2 - Public AI Assistant")
st.write("Welcome to V2! Now with Image Analysis & Chat support.")

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

# Chat input from user
if prompt := st.chat_input("Ask ARIS anything or describe the image..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response from Groq
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            # Preparing message content based on whether an image was uploaded
            if base64_image:
                messages_payload = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ]
                model_to_use = "llama-3.2-11b-vision-preview"
            else:
                messages_payload = [
                    {
                        "role": "user",
                        "content": prompt,
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
