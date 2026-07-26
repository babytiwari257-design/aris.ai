import streamlit as st
from groq import Groq

st.set_page_config(page_title="ARIS AI", page_icon="🤖")

st.title("🤖 ARIS - Public AI Assistant")
st.write("Welcome! Chat with ARIS from anywhere.")

# Streamlit secrets se key uthane ka secure tarika
api_key = st.secrets["GROQ_API_KEY"]

client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask ARIS anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            system_instruction = "You are ARIS, a helpful, intelligent, and friendly web-based AI assistant created by Mayank."
            messages = [{"role": "system", "content": system_instruction}]
            for m in st.session_state.messages:
                messages.append({"role": m["role"], "content": m["content"]})

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages
            )

            reply = response.choices[0].message.content
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"An error occurred: {e}")
