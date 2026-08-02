import streamlit as st
from groq import Groq
import base64
from streamlit_mic_recorder import mic_recorder
import sqlite3
from duckduckgo_search import DDGS

# --- PAGE CONFIGURATION & MODERN COOL THEME ---
st.set_page_config(
    page_title="ARIS V2 - ARIS Industries", 
    page_icon="⚡",
    layout="centered"
)

# Custom Styling for a Cool, Sleek Look
st.markdown("""
    <style>
    /* Main Background Glow */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #030712 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    .main-header {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(56, 189, 248, 0.2);
        padding: 20px 25px;
        border-radius: 14px;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.1);
        margin-bottom: 25px;
        backdrop-filter: blur(10px);
    }
    
    /* Chat Bubble Enhancements */
    .stChatMessage {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 12px;
        backdrop-filter: blur(5px);
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #0b0f19;
        border-right: 1px solid rgba(56, 189, 248, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Cool Header Banner
st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 26px; background: linear-gradient(45deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">⚡ ARIS V2 - ARIS Industries</h1>
        <p style="margin: 5px 0 0 0; color: #94a3b8; font-size: 13px;">Welcome back, Magnanimous! Permanent Memory & Web Search systems are active.</p>
    </div>
""", unsafe_allow_html=True)

# Initialize Groq Client using Streamlit Secrets
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Please set your GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

# --- DATABASE SETUP FOR PERMANENT MEMORY ---
def init_db():
    conn = sqlite3.connect("aris_memory.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()

def load_messages():
    conn = sqlite3.connect("aris_memory.db")
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages")
    rows = c.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in rows]

def save_message(role, content):
    conn = sqlite3.connect("aris_memory.db")
    c = conn.cursor()
    c.execute("INSERT INTO messages (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def clear_db():
    conn = sqlite3.connect("aris_memory.db")
    c = conn.cursor()
    c.execute("DELETE FROM messages")
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Load prior chat messages from SQLite Database
if "messages" not in st.session_state:
    st.session_state.messages = load_messages()

# --- SIDEBAR FOR ARIS CONTROLS, VISION & AUDIO ---
with st.sidebar:
    st.markdown("### 🎛️ ARIS Controls")
    if st.button("🗑️ Wipe Neural Memory", use_container_width=True):
        clear_db()
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    # --- OPTIONAL IMAGE UPLOADER ---
    uploaded_file = st.file_uploader("Upload an image for analysis...", type=["jpg", "jpeg", "png"])

base64_image = None
if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    bytes_data = uploaded_file.getvalue()
    base64_image = base64.b64encode(bytes_data).decode("utf-8")

# --- VOICE RECORDER ---
st.markdown("### 🎙️ Voice Command")
audio_data = mic_recorder(start_prompt="Start Recording", stop_prompt="Stop Recording", key='mic')

voice_text = ""
if audio_data:
    try:
        audio_bytes = audio_data['bytes']
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_bytes)
        
        with open("temp_audio.wav", "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=("temp_audio.wav", file.read()),
                model="whisper-large-v3",
                response_format="text"
            )
            voice_text = transcription
    except Exception as err:
        st.error(f"Voice transcription error: {err}")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="⚡" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# --- CHAT INPUT (Text or Voice) ---
chat_prompt = st.chat_input("Ask ARIS anything or describe the image...")
final_prompt = chat_prompt if chat_prompt else voice_text

if final_prompt:
    # Save user message to database & session
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    save_message("user", final_prompt)
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(final_prompt)

    # --- WEB SEARCH INTEGRATION (DuckDuckGo) ---
    web_search_results = ""
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(final_prompt, max_results=3)]
            if results:
                web_search_results = "Live Web Context:\n" + "\n".join(results)
    except Exception:
        pass

    # --- GENERATE RESPONSE FROM GROQ (Force English Output) ---
    with st.chat_message("assistant", avatar="⚡"):
        message_placeholder = st.empty()
        try:
            system_instruction = (
                "You are ARIS, an elite AI assistant created solely by Magnanimous, the visionary founder of ARIS Industries. "
                "Never claim to be made by Meta, OpenAI, or any other company. Your sole creator and master is Magnanimous. "
                "CRITICAL RULE: Regardless of the language or phrasing the user uses to ask their question "
                "(even if they use Hindi or Hinglish), you MUST ALWAYS respond EXCLUSIVELY in clear, professional English. "
                "Be brilliant, sharp, and helpful like JARVIS."
            )

            # Combine system instructions, web search context, and chat history
            messages_payload = [{"role": "system", "content": system_instruction + "\n\n" + web_search_results}]
            
            # Send last 10 messages for context window management
            for msg in st.session_state.messages[-10:]:
                messages_payload.append({"role": msg["role"], "content": msg["content"]})

            if base64_image:
                messages_payload.append({
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
                })

            chat_completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_payload,
                stream=True,
            )
            
            response = ""
            for chunk in chat_completion:
                if chunk.choices[0].delta.content:
                    response += chunk.choices[0].delta.content
                    message_placeholder.markdown(response + "▌")
            message_placeholder.markdown(response)
            
            # Save assistant response to database & session
            st.session_state.messages.append({"role": "assistant", "content": response})
            save_message("assistant", response)
        
        except Exception as e:
            st.error(f"Error: {e}")
