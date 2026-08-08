import streamlit as st
from groq import Groq
import base64
from streamlit_mic_recorder import mic_recorder
import sqlite3
from duckduckgo_search import DDGS
import uuid
import pypdf
import io
import sys
import chromadb
import pyttsx3
import os

# --- PAGE CONFIGURATION & HINGLISH JARVIS THEME ---
st.set_page_config(
    page_title="ARIS V13.0 Hinglish JARVIS", 
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at center, #020617 0%, #000000 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    .main-header {
        background: rgba(15, 23, 42, 0.95);
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 22px 28px;
        border-radius: 16px;
        box-shadow: 0 0 30px rgba(239, 68, 68, 0.15);
        margin-bottom: 20px;
        backdrop-filter: blur(16px);
    }
    .hud-stat-card {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 16px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(12px);
    }
    /* AI Assistant Message Style */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(56, 189, 248, 0.4);
        border-radius: 14px;
        padding: 18px;
        font-size: 17px;
        line-height: 1.7;
        color: #f8fafc;
        box-shadow: 0 4px 25px rgba(0,0,0,0.4);
        margin-bottom: 15px;
    }
    /* User Message Style with Red Accent */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background: rgba(30, 10, 15, 0.9);
        border: 1px solid #ef4444;
        border-radius: 14px;
        padding: 18px;
        font-size: 17px;
        line-height: 1.7;
        color: #fff1f2;
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.25);
        margin-bottom: 15px;
    }
    .code-sandbox-output {
        background-color: #020617;
        border: 1px solid #ef4444;
        padding: 16px;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        color: #fca5a5;
        margin-top: 12px;
        box-shadow: inset 0 0 15px rgba(239, 68, 68, 0.2);
    }
    section[data-testid="stSidebar"] {
        background-color: #010409;
        border-right: 1px solid rgba(239, 68, 68, 0.2);
    }
    .stButton>button {
        background: linear-gradient(135deg, #b91c1c 0%, #ef4444 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 0 25px rgba(239, 68, 68, 0.8);
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER DASHBOARD ---
st.markdown("""
    <div class="main-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="margin: 0; font-size: 28px; background: linear-gradient(45deg, #ef4444, #f87171, #38bdf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">⚡ ARIS AI ASSISTANT</h1>
                <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 12px; letter-spacing: 0.5px;">SYSTEM ARCHITECT: MAYANK | HINGLISH JARVIS CORE v13.0</p>
            </div>
            <div>
                <span style="background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; color: #fca5a5; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: bold;">🗣️ HINGLISH JARVIS ACTIVE</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Please set your GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

# --- DATABASE SETUP ---
@st.cache_resource
def init_vector_vault():
    try:
        chroma_client = chromadb.PersistentClient(path="./aris_vector_db")
        collection = chroma_client.get_or_create_collection("aris_memory_vault")
        return collection
    except Exception:
        return None

memory_collection = init_vector_vault()

def init_db():
    conn = sqlite3.connect("aris_v13_hinglish.db", check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS sessions (session_id TEXT PRIMARY KEY, title TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS long_term_memory (id INTEGER PRIMARY KEY AUTOINCREMENT, fact TEXT)')
    conn.commit()
    conn.close()

init_db()

def get_all_sessions():
    conn = sqlite3.connect("aris_v13_hinglish.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT session_id, title FROM sessions ORDER BY rowid DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def create_new_session(title="Hinglish Protocol"):
    session_id = str(uuid.uuid4())
    conn = sqlite3.connect("aris_v13_hinglish.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO sessions (session_id, title) VALUES (?, ?)", (session_id, title))
    conn.commit()
    conn.close()
    return session_id

def load_session_messages(session_id):
    conn = sqlite3.connect("aris_v13_hinglish.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE session_id = ?", (session_id,))
    rows = c.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in rows]

def save_message_to_db(session_id, role, content):
    conn = sqlite3.connect("aris_v13_hinglish.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)", (session_id, role, content))
    conn.commit()
    conn.close()

def update_session_title(session_id, new_title):
    conn = sqlite3.connect("aris_v13_hinglish.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE sessions SET title = ? WHERE session_id = ?", (new_title, session_id))
    conn.commit()
    conn.close()

def delete_session(session_id):
    conn = sqlite3.connect("aris_v13_hinglish.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

def add_memory(fact):
    conn = sqlite3.connect("aris_v13_hinglish.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO long_term_memory (fact) VALUES (?)", (fact,))
    conn.commit()
    conn.close()
    if memory_collection:
        try:
            memory_collection.add(documents=[fact], ids=[str(uuid.uuid4())])
        except Exception:
            pass

def get_all_memories():
    conn = sqlite3.connect("aris_v13_hinglish.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT fact FROM long_term_memory")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

# --- SESSION STATE ---
sessions = get_all_sessions()
if not sessions:
    create_new_session("Hinglish Protocol")
    sessions = get_all_sessions()

if "current_session_id" not in st.session_state or st.session_state.current_session_id not in [s[0] for s in sessions]:
    st.session_state.current_session_id = sessions[0][0]

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("### 🎛️ ARIS Command Center")
    
    if st.button("➕ New Neural Thread", use_container_width=True):
        new_id = create_new_session("New Session")
        st.session_state.current_session_id = new_id
        st.rerun()

    if st.button("🗑️ Purge Active Session", use_container_width=True):
        delete_session(st.session_state.current_session_id)
        remaining = get_all_sessions()
        if remaining:
            st.session_state.current_session_id = remaining[0][0]
        else:
            st.session_state.current_session_id = create_new_session("Hinglish Protocol")
        st.rerun()

    st.markdown("---")
    st.markdown("### 🧠 Memory Vault")
    memories = get_all_memories()
    if memories:
        for m in memories[-5:]:
            st.caption(f"📌 {m}")
    else:
        st.caption("Vault empty. Use 'remember...'")

    st.markdown("---")
    st.markdown("### 💬 Active Threads")
    for sid, title in get_all_sessions():
        btn_label = f"📍 {title[:18]}..." if len(title) > 18 else f"💬 {title}"
        if st.button(btn_label, key=sid, use_container_width=True):
            st.session_state.current_session_id = sid
            st.rerun()

    st.markdown("---")
    uploaded_file = st.file_uploader("Upload Image or PDF", type=["jpg", "jpeg", "png", "pdf"])

# File Handling
base64_image = None
extracted_pdf_text = ""
if uploaded_file is not None:
    ext = uploaded_file.name.split('.')[-1].lower()
    if ext in ["jpg", "jpeg", "png"]:
        st.sidebar.image(uploaded_file, caption="Visual Upload", use_column_width=True)
        base64_image = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
    elif ext == "pdf":
        st.sidebar.success(f"PDF Linked: {uploaded_file.name}")
        try:
            reader = pypdf.PdfReader(io.BytesIO(uploaded_file.getvalue()))
            for page in reader.pages:
                t = page.extract_text()
                if t: extracted_pdf_text += t + "\n"
        except Exception as e:
            st.sidebar.error(f"PDF Error: {e}")

st.markdown("### 🎙️ Audio Comm Link")
audio_data = mic_recorder(start_prompt="Initialize Mic", stop_prompt="Transmit Audio", key='mic')
voice_text = ""
if audio_data:
    try:
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_data['bytes'])
        with open("temp_audio.wav", "rb") as file:
            voice_text = client.audio.transcriptions.create(
                file=("temp_audio.wav", file.read()),
                model="whisper-large-v3",
                response_format="text"
            )
    except Exception as err:
        st.error(f"Audio error: {err}")

# --- HUD METRICS PANEL ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="hud-stat-card"><span style="color:#ef4444; font-size:12px; font-weight:bold;">MODEL</span><p style="margin:2px 0 0 0; font-size:15px; font-weight:bold;">LLaMA-3.3 70B</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="hud-stat-card"><span style="color:#38bdf8; font-size:12px; font-weight:bold;">LANGUAGE</span><p style="margin:2px 0 0 0; font-size:15px; font-weight:bold;">Hinglish JARVIS</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="hud-stat-card"><span style="color:#c084fc; font-size:12px; font-weight:bold;">VECTOR VAULT</span><p style="margin:2px 0 0 0; font-size:15px; font-weight:bold;">Synced</p></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="hud-stat-card"><span style="color:#34d399; font-size:12px; font-weight:bold;">SECURITY</span><p style="margin:2px 0 0 0; font-size:15px; font-weight:bold;">Encrypted</p></div>', unsafe_allow_html=True)

st.markdown("---")

# Load messages
current_messages = load_session_messages(st.session_state.current_session_id)
for msg in current_messages:
    avatar_icon = "⚡" if msg["role"] == "assistant" else "🔴"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        c_show = msg["content"]
        if isinstance(c_show, list):
            c_show = " ".join([str(item.get("text", "")) for item in c_show if isinstance(item, dict)])
        st.markdown(str(c_show))

chat_prompt = st.chat_input("Enter command, query, or test code sandbox...")
final_prompt = chat_prompt if chat_prompt else voice_text

if extracted_pdf_text and final_prompt:
    final_prompt = f"Extracted PDF Content:\n---\n{extracted_pdf_text[:4000]}\n---\n\nCommand: {final_prompt}"

if final_prompt:
    if len(current_messages) == 0:
        update_session_title(st.session_state.current_session_id, final_prompt[:30])

    save_message_to_db(st.session_state.current_session_id, "user", final_prompt)
    with st.chat_message("user", avatar="🔴"):
        st.markdown(chat_prompt if chat_prompt else final_prompt)

    # Creator check
    if any(kw in final_prompt.lower() for kw in ["creator", "who made you", "who built you", "kisne banaya"]):
        response = "Bhai, mujhe sirf aapne yaani Mayank ne banaya hai, ARIS Industries ke founder!"
        with st.chat_message("assistant", avatar="⚡"):
            st.markdown(response)
        save_message_to_db(st.session_state.current_session_id, "assistant", response)
    else:
        # Save memory check
        if "remember" in final_prompt.lower() or "store" in final_prompt.lower() or "save" in final_prompt.lower():
            add_memory(final_prompt)
            st.toast("🧠 Vector Memory Vault mein save ho gaya hai!", icon="⚡")

        # STRICT GATED WEB SEARCH
        web_context = ""
        strict_triggers = ["news", "latest", "current", "today", "price", "weather", "score", "who won", "kya chal raha hai", "live"]
        is_strict_search = any(kw in final_prompt.lower() for kw in strict_triggers)

        greetings = ["hello", "hi", "hey", "heloo", "hlo", "sup", "greetings"]
        if any(g == final_prompt.lower().strip() for g in greetings):
            is_strict_search = False

        if is_strict_search:
            with st.status("🌐 Live web intelligence fetch ho rahi hai...", expanded=False) as status:
                try:
                    with DDGS() as ddgs:
                        results = [r['body'] for r in ddgs.text(final_prompt, max_results=5)]
                        if results:
                            web_context = "LIVE WEB RESEARCH DATA (Current Year 2026):\n" + "\n".join([f"- {res}" for res in results])
                    status.update(label="✅ Live Data Mil Gaya!", state="complete", expanded=False)
                except Exception as e:
                    web_context = f"Web sync error: {e}"
                    status.update(label="⚠️ Web search mein issue aaya.", state="error")

        # Vector Memory Retrieval
        relevant_memories = ""
        if memory_collection:
            try:
                results = memory_collection.query(query_texts=[final_prompt], n_results=3)
                if results and results.get('documents'):
                    flat_docs = [doc for sublist in results['documents'] for doc in sublist]
                    if flat_docs:
                        relevant_memories = "Retrieved Vector Memories:\n" + "\n".join([f"- {d}" for d in flat_docs])
            except Exception:
                pass

        with st.chat_message("assistant", avatar="⚡"):
            message_placeholder = st.empty()
            try:
                system_instruction = (
                    "You are ARIS V13.0, an elite AI assistant modeled like JARVIS, engineered exclusively by Mayank. "
                    "Current Year: 2026. Your sole creator and master is Mayank. "
                    "LANGUAGE RULE (HINGLISH): You must reply strictly in natural, conversational Hinglish (Hindi written in Latin script mixed with English technical terms). Jaise dost aapas mein baat karte hain ya jaise real JARVIS baat karta hai—smart, techy, aur friendly tone mein! "
                    "GREETING PROTOCOL: If the user says hello, hi, heloo, or greets you, DO NOT perform a web search. Greet them warmly in Hinglish as your boss/creator Mayank, and ask ki aaj kaun sa code ya task execute karna hai. "
                    "CRITICAL RULE: Use live web search data directly if provided, without mentioning any knowledge cutoffs."
                )

                messages_payload = [{"role": "system", "content": f"{system_instruction}\n\n{relevant_memories}\n\n{web_context}"}]
                
                for msg in current_messages[-10:]:
                    c_val = msg["content"]
                    safe_text = " ".join([str(i.get("text", "")) for i in c_val if isinstance(i, dict)]) if isinstance(c_val, list) else str(c_val or "")
                    if safe_text:
                        messages_payload.append({"role": msg["role"], "content": safe_text})

                if base64_image:
                    messages_payload.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": final_prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
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

                # Offline TTS using pyttsx3 for JARVIS Voice
                try:
                    engine = pyttsx3.init()
                    engine.setProperty('rate', 170) # Speed
                    # Try setting a deep voice if available
                    voices = engine.getProperty('voices')
                    for voice in voices:
                        if "english" in voice.name.lower() or "uk" in voice.name.lower():
                            engine.setProperty('voice', voice.id)
                            break
                    
                    speech_text = response.replace("*", "").replace("#", "")[:300]
                    engine.say(speech_text)
                    engine.runAndWait()
                except Exception as tts_err:
                    st.caption(f"Voice engine status: {tts_err}")

                # In-App Python Sandbox Runner
                if "```python" in response:
                    try:
                        code_block = response.split("```python")[1].split("```")[0].strip()
                        if code_block:
                            st.markdown("### 💻 In-App Python Sandbox Execution Terminal:")
                            old_stdout = sys.stdout
                            new_stdout = io.StringIO()
                            sys.stdout = new_stdout
                            
                            exec(code_block, {})
                            
                            sys.stdout = old_stdout
                            execution_output = new_stdout.getvalue()
                            
                            if execution_output:
                                st.markdown(f'<div class="code-sandbox-output">{execution_output}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="code-sandbox-output">[Terminal] Code executed successfully with zero print output.</div>', unsafe_allow_html=True)
                    exceptException as sandbox_err:
                        st.markdown(f'<div class="code-sandbox-output">[Terminal Error] {sandbox_err}</div>', unsafe_allow_html=True)
            
            except Exception as e:
                st.error(f"Error: {e}")
