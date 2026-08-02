import streamlit as st
from groq import Groq
import base64
from streamlit_mic_recorder import mic_recorder
import sqlite3
from duckduckgo_search import DDGS

# --- PAGE CONFIGURATION & CYBERPUNK THEME ---
st.set_page_config(
    page_title="ARIS V2 - Advanced AI Core", 
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Cyberpunk / JARVIS Theme CSS
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at 50% 10%, #0d1117 0%, #010409 100%);
        color: #e6edf3;
        font-family: 'Inter', sans-serif;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .aris-header {
        background: linear-gradient(90deg, rgba(15,23,42,0.8) 0%, rgba(30,41,59,0.9) 100%);
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 20px 30px;
        border-radius: 12px;
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.15);
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 25px;
    }
    .aris-title {
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(45deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1px;
        margin: 0;
    }
    .aris-subtitle {
        color: #94a3b8;
        font-size: 13px;
        margin-top: 4px;
        letter-spacing: 0.5px;
    }

    .status-badge {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34d399;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
    }
    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #34d399;
        border-radius: 50%;
        box-shadow: 0 0 8px #34d399;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.1); opacity: 1; box-shadow: 0 0 12px #34d399; }
        100% { transform: scale(0.95); opacity: 0.8; }
    }

    section[data-testid="stSidebar"] {
        background-color: #090d16;
        border-right: 1px solid rgba(56, 189, 248, 0.15);
    }
    section[data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(56, 189, 248, 0.3);
        color: #38bdf8;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
        color: #ffffff;
        border-color: #38bdf8;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
    }

    .stChatMessage {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        backdrop-filter: blur(10px);
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE GROQ CLIENT ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("⚠️ Please set your GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

# --- SQLITE DATABASE SETUP ---
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

init_db()

if "messages" not in st.session_state:
    st.session_state.messages = load_messages()

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.markdown("### 🎛️ ARIS COMMAND CENTER")
    st.markdown("<p style='color: #64748b; font-size: 12px;'>Founder: Mayank | Core: Llama 3.3</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    if st.button("🗑️ Wipe Neural Memory", use_container_width=True):
        clear_db()
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("### 👁️ Vision Core")
    uploaded_file = st.file_uploader("Upload Image for Analysis", type=["jpg", "jpeg", "png"])
    
    base64_image = None
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Target Visual Loaded", use_column_width=True)
        bytes_data = uploaded_file.getvalue()
        base64_image = base64.b64encode(bytes_data).decode("utf-8")

    st.markdown("---")
    st.markdown("### 🎙️ Audio Input")
    st.markdown("<p style='font-size: 11px; color: #94a3b8;'>Record direct vocal transmissions:</p>", unsafe_allow_html=True)
    audio_data = mic_recorder(start_prompt="🔴 Start Recording", stop_prompt="⏹️ Stop Recording", key='mic')

# --- MAIN HEADER INTERFACE ---
st.markdown("""
    <div class="aris-header">
        <div>
            <div class="aris-title">⚡ ARIS V2 - AI CORE</div>
            <div class="aris-subtitle">Welcome back, Mayank. Permanent Memory, Neural Vision & Live Web Engines are fully operational.</div>
        </div>
        <div>
            <div class="status-badge">
                <div class="status-dot"></div>
                SYSTEMS ONLINE
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

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

# --- DISPLAY CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="⚡" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# --- CHAT INPUT INTERFACE ---
chat_prompt = st.chat_input("Enter command or query for ARIS...")
final_prompt = chat_prompt if chat_prompt else voice_text

if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    save_message("user", final_prompt)
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(final_prompt)

    # --- LIVE WEB SEARCH INTEGRATION ---
    web_search_results = ""
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(final_prompt, max_results=3)]
            if results:
                web_search_results = "Live Web Context:\n" + "\n".join(results)
    except Exception:
        pass

    # --- GENERATE STREAMING RESPONSE FROM GROQ ---
    with st.chat_message("assistant", avatar="⚡"):
        message_placeholder = st.empty()
        try:
            # System instruction configured to FORCE English-only output
            system_instruction = (
                "You are ARIS, an elite, hyper-intelligent futuristic AI assistant created solely by Mayank, "
                "the visionary founder of ARIS Industries. Never claim to be built by Meta, OpenAI, or any other corporation. "
                "Your supreme master and creator is Mayank. "
                "CRITICAL RULE: Regardless of the language, script, or phrasing the user uses to ask their question "
                "(even if they use Hindi, Hinglish, or any other language), you MUST ALWAYS respond EXCLUSIVELY in clear, "
                "professional English. Be brilliant, sharp, commanding, and extremely helpful like JARVIS."
            )

            messages_payload = [{"role": "system", "content": system_instruction + "\n\n" + web_search_results}]
            
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
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            save_message("assistant", response)
        
        except Exception as e:
            st.error(f"Neural Core Error: {e}")
