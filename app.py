import streamlit as st
from groq import Groq
import base64
from streamlit_mic_recorder import mic_recorder
import sqlite3
from duckduckgo_search import DDGS
import uuid

# --- PAGE CONFIGURATION & MODERN COOL THEME ---
st.set_page_config(
    page_title="ARIS V3 - ARIS Industries", 
    page_icon="⚡",
    layout="centered"
)

# --- HIDE STREAMLIT BRANDING, FORK & GITHUB ICON ---
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Custom Styling for a Cool, Sleek Look
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #030712 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    .main-header {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(56, 189, 248, 0.2);
        padding: 20px 25px;
        border-radius: 14px;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.1);
        margin-bottom: 25px;
        backdrop-filter: blur(10px);
    }
    .stChatMessage {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 12px;
        backdrop-filter: blur(5px);
    }
    section[data-testid="stSidebar"] {
        background-color: #0b0f19;
        border-right: 1px solid rgba(56, 189, 248, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 26px; background: linear-gradient(45deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">⚡ ARIS V3 - ARIS Industries</h1>
        <p style="margin: 5px 0 0 0; color: #94a3b8; font-size: 13px;">Welcome back, User! Secure Multi-Modal & Web Search systems are active.</p>
    </div>
""", unsafe_allow_html=True)

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Please set your GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

# --- SQLITE DATABASE SETUP FOR MULTI-CHAT HISTORY ---
def init_db():
    conn = sqlite3.connect("aris_multichat.db", check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            title TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_all_sessions():
    conn = sqlite3.connect("aris_multichat.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT session_id, title FROM sessions ORDER BY rowid DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def create_new_session(title="New Chat"):
    session_id = str(uuid.uuid4())
    conn = sqlite3.connect("aris_multichat.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO sessions (session_id, title) VALUES (?, ?)", (session_id, title))
    conn.commit()
    conn.close()
    return session_id

def load_session_messages(session_id):
    conn = sqlite3.connect("aris_multichat.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE session_id = ?", (session_id,))
    rows = c.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in rows]

def save_message_to_db(session_id, role, content):
    conn = sqlite3.connect("aris_multichat.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)", (session_id, role, content))
    conn.commit()
    conn.close()

def update_session_title(session_id, new_title):
    conn = sqlite3.connect("aris_multichat.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE sessions SET title = ? WHERE session_id = ?", (new_title, session_id))
    conn.commit()
    conn.close()

def delete_session(session_id):
    conn = sqlite3.connect("aris_multichat.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

# --- SESSION STATE MANAGEMENT FOR CHATS ---
sessions = get_all_sessions()
if not sessions:
    initial_id = create_new_session("Welcome Chat")
    sessions = get_all_sessions()

if "current_session_id" not in st.session_state or st.session_state.current_session_id not in [s[0] for s in sessions]:
    st.session_state.current_session_id = sessions[0][0]

# --- SIDEBAR FOR CHAT HISTORY & CONTROLS ---
with st.sidebar:
    st.markdown("### 🎛️ ARIS Controls")
    
    if st.button("➕ New Chat Thread", use_container_width=True):
        new_id = create_new_session("New Chat")
        st.session_state.current_session_id = new_id
        st.rerun()

    if st.button("🗑️ Wipe Current Chat", use_container_width=True):
        delete_session(st.session_state.current_session_id)
        remaining = get_all_sessions()
        if remaining:
            st.session_state.current_session_id = remaining[0][0]
        else:
            st.session_state.current_session_id = create_new_session("New Chat")
        st.rerun()

    st.markdown("---")
    st.markdown("### 💬 Chat History")
    
    current_sessions = get_all_sessions()
    for sid, title in current_sessions:
        btn_label = f"📍 {title[:22]}..." if len(title) > 22 else f"💬 {title}"
        if st.button(btn_label, key=sid, use_container_width=True):
            st.session_state.current_session_id = sid
            st.rerun()

    st.markdown("---")
    uploaded_file = st.file_uploader("Upload an image for analysis...", type=["jpg", "jpeg", "png"])

base64_image = None
if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    bytes_data = uploaded_file.getvalue()
    base64_image = base64.b64encode(bytes_data).decode("utf-8")

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

# Load messages for the active session
current_messages = load_session_messages(st.session_state.current_session_id)

for message in current_messages:
    with st.chat_message(message["role"], avatar="⚡" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

chat_prompt = st.chat_input("Ask ARIS anything or describe the image...")
final_prompt = chat_prompt if chat_prompt else voice_text

if final_prompt:
    if len(current_messages) == 0:
        update_session_title(st.session_state.current_session_id, final_prompt[:30])

    save_message_to_db(st.session_state.current_session_id, "user", final_prompt)
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(final_prompt)

    prompt_lower = final_prompt.lower()
    creator_keywords = ["creator", "who made you", "who built you", "kisne banaya", "tumhe kisne banaya", "owner", "founder"]
    is_creator_query = any(kw in prompt_lower for kw in creator_keywords)

    if is_creator_query:
        response = "I was created solely by Mayank, the visionary founder of ARIS Industries."
        with st.chat_message("assistant", avatar="⚡"):
            st.markdown(response)
        save_message_to_db(st.session_state.current_session_id, "assistant", response)
    else:
        web_search_results = ""
        try:
            with DDGS() as ddgs:
                results = [r['body'] for r in ddgs.text(final_prompt, max_results=3)]
                if results:
                    web_search_results = "Live Web Context:\n" + "\n".join(results)
        except Exception:
            pass

        with st.chat_message("assistant", avatar="⚡"):
            message_placeholder = st.empty()
            try:
                system_instruction = (
                    "You are ARIS, an elite AI assistant created solely by Mayank, the visionary founder of ARIS Industries. "
                    "Never claim to be made by Meta, OpenAI, or any other company. Your sole creator and master is Mayank. "
                    "CRITICAL RULE: Regardless of the language or phrasing the user uses to ask their question "
                    "(even if they use Hindi or Hinglish), you MUST ALWAYS respond EXCLUSIVELY in clear, professional English. "
                    "Be brilliant, sharp, and helpful like JARVIS."
                )

                messages_payload = [{"role": "system", "content": system_instruction + "\n\n" + web_search_results}]
                
                # Safely parse past messages to prevent list-to-string 400 error crash
                for msg in current_messages[-10:]:
                    safe_content = str(msg["content"]) if not isinstance(msg["content"], list) else str(msg["content"][0].get("text", ""))
                    messages_payload.append({"role": msg["role"], "content": safe_content})

                # Append current prompt with image payload if provided
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
                else:
                    messages_payload.append({"role": "user", "content": final_prompt})

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
                
                save_message_to_db(st.session_state.current_session_id, "assistant", response)
            
            except Exception as e:
                st.error(f"Error: {e}")
