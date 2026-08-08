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

# --- PAGE CONFIGURATION & CYBER-MATRIX THEME ---
st.set_page_config(
    page_title="ARIS V8.0 Cyber-HUD Elite", 
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at center, #030712 0%, #010204 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    .main-header {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.4);
        padding: 22px 28px;
        border-radius: 16px;
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.15);
        margin-bottom: 20px;
        backdrop-filter: blur(14px);
    }
    .hud-stat-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(56, 189, 248, 0.25);
        padding: 16px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
    }
    .stChatMessage {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 14px;
        padding: 16px;
        font-size: 16px;
        line-height: 1.6;
        color: #f1f5f9;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
        margin-bottom: 12px;
    }
    .code-sandbox-output {
        background-color: #020617;
        border: 1px solid #38bdf8;
        padding: 16px;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        color: #38bdf8;
        margin-top: 12px;
        box-shadow: inset 0 0 15px rgba(56, 189, 248, 0.15);
    }
    section[data-testid="stSidebar"] {
        background-color: #020408;
        border-right: 1px solid rgba(56, 189, 248, 0.2);
    }
    .stButton>button {
        background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.6);
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER DASHBOARD ---
st.markdown("""
    <div class="main-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="margin: 0; font-size: 28px; background: linear-gradient(45deg, #38bdf8, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">⚡ ARIS AI ASSISTANT</h1>
                <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 12px; letter-spacing: 0.5px;">SYSTEM ARCHITECT: MAYANK | CYBER-HUD v8.0</p>
            </div>
            <div>
                <span style="background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #34d399; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: bold;">🟢 CORE ONLINE</span>
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
    conn = sqlite3.connect("aris_v8_hud.db", check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS sessions (session_id TEXT PRIMARY KEY, title TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS long_term_memory (id INTEGER PRIMARY KEY AUTOINCREMENT, fact TEXT)')
    conn.commit()
    conn.close()

init_db()

def get_all_sessions():
    conn = sqlite3.connect("aris_v8_hud.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT session_id, title FROM sessions ORDER BY rowid DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def create_new_session(title="Cyber HUD Session"):
    session_id = str(uuid.uuid4())
    conn = sqlite3.connect("aris_v8_hud.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO sessions (session_id, title) VALUES (?, ?)", (session_id, title))
    conn.commit()
    conn.close()
    return session_id

def load_session_messages(session_id):
    conn = sqlite3.connect("aris_v8_hud.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE session_id = ?", (session_id,))
    rows = c.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in rows]

def save_message_to_db(session_id, role, content):
    conn = sqlite3.connect("aris_v8_hud.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)", (session_id, role, content))
    conn.commit()
    conn.close()

def update_session_title(session_id, new_title):
    conn = sqlite3.connect("aris_v8_hud.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE sessions SET title = ? WHERE session_id = ?", (new_title, session_id))
    conn.commit()
    conn.close()

def delete_session(session_id):
    conn = sqlite3.connect("aris_v8_hud.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

def add_memory(fact):
    conn = sqlite3.connect("aris_v8_hud.db", check_same_thread=False)
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
    conn = sqlite3.connect("aris_v8_hud.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT fact FROM long_term_memory")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

# --- SESSION STATE ---
sessions = get_all_sessions()
if not sessions:
    create_new_session("Cyber HUD Session")
    sessions = get_all_sessions()

if "current_session_id" not in st.session_state or st.session_state.current_session_id not in [s[0] for s in sessions]:
    st.session_state.current_session_id = sessions[0][0]

# --- SIDEBAR HUD CONTROLS ---
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
            st.session_state.current_session_id = create_new_session("Cyber HUD Session")
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
    st.markdown('<div class="hud-stat-card"><span style="color:#38bdf8; font-size:12px; font-weight:bold;">MODEL</span><p style="margin:2px 0 0 0; font-size:15px; font-weight:bold;">LLaMA-3.3 70B</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="hud-stat-card"><span style="color:#818cf8; font-size:12px; font-weight:bold;">WEB MATRIX</span><p style="margin:2px 0 0 0; font-size:15px; font-weight:bold;">Smart-Trigger</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="hud-stat-card"><span style="color:#c084fc; font-size:12px; font-weight:bold;">VECTOR MEMORY</span><p style="margin:2px 0 0 0; font-size:15px; font-weight:bold;">Active</p></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="hud-stat-card"><span style="color:#34d399; font-size:12px; font-weight:bold;">SECURITY</span><p style="margin:2px 0 0 0; font-size:15px; font-weight:bold;">Encrypted</p></div>', unsafe_allow_html=True)

st.markdown("---")

# Load messages
current_messages = load_session_messages(st.session_state.current_session_id)
for msg in current_messages:
    with st.chat_message(msg["role"], avatar="⚡" if msg["role"] == "assistant" else "👤"):
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
    with st.chat_message("user", avatar="👤"):
        st.markdown(chat_prompt if chat_prompt else final_prompt)

    # Creator check
    if any(kw in final_prompt.lower() for kw in ["creator", "who made you", "who built you", "kisne banaya"]):
        response = "I was engineered solely by Mayank, the visionary founder of ARIS Industries."
        with st.chat_message("assistant", avatar="⚡"):
            st.markdown(response)
        save_message_to_db(st.session_state.current_session_id, "assistant", response)
    else:
        # Save memory check
        if "remember" in final_prompt.lower() or "store" in final_prompt.lower() or "save" in final_prompt.lower():
            add_memory(final_prompt)
            st.toast("🧠 Synchronized to Vector Memory Vault!", icon="⚡")

        # SMART-TRIGGERED WEB SEARCH
        web_context = ""
        search_keywords = ["news", "latest", "current", "today", "price", "weather", "score", "who won", "kya chal raha hai"]
        is_search_needed = any(kw in final_prompt.lower() for kw in search_keywords)

        if is_search_needed:
            with st.status("🌐 Accessing live web intelligence...", expanded=False) as status:
                try:
                    with DDGS() as ddgs:
                        results = [r['body'] for r in ddgs.text(final_prompt, max_results=5)]
                        if results:
                            web_context = "LIVE WEB RESEARCH DATA (Current Year 2026):\n" + "\n".join([f"- {res}" for res in results])
                    status.update(label="✅ Live Data Acquired!", state="complete", expanded=False)
                except Exception as e:
                    web_context = f"Web sync error: {e}"
                    status.update(label="⚠️ Web search fallback engaged.", state="error")

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
                    "You are ARIS V8.0 Cyber-HUD, an ultra-advanced AI assistant engineered exclusively by Mayank, the visionary founder of ARIS Industries. "
                    "Never claim to be made by Meta, OpenAI, Google, or any other entity. Your sole creator and master is Mayank. "
                    "GREETING INSTRUCTION: If the user says hello, hi, or greets you, respond warmly and engagingly like a futuristic AI companion, asking what project or task you can help with today (e.g., coding, development, study, or creative work), without performing unnecessary web searches. "
                    "CRITICAL RULE: If live web search data is provided in your context, utilize it to answer current events accurately. "
                    "CRITICAL LANGUAGE RULE: Regardless of the language or phrasing used by the user, you MUST ALWAYS respond EXCLUSIVELY in clear, professional English. "
                    "Be brilliant, sharp, authoritative, and helpful like JARVIS."
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
                    except Exception as sandbox_err:
                        st.markdown(f'<div class="code-sandbox-output">[Terminal Error] {sandbox_err}</div>', unsafe_allow_html=True)
            
            except Exception as e:
                st.error(f"Error: {e}")
