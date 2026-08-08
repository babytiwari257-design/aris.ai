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

# --- PAGE CONFIGURATION & THEME ---
st.set_page_config(
    page_title="ARIS V5 Ultimate - ARIS Industries", 
    page_icon="⚡",
    layout="centered"
)

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
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.15);
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
    .code-sandbox-output {
        background-color: #030712;
        border: 1px solid #38bdf8;
        padding: 15px;
        border-radius: 8px;
        font-family: monospace;
        color: #38bdf8;
        margin-top: 10px;
    }
    section[data-testid="stSidebar"] {
        background-color: #0b0f19;
        border-right: 1px solid rgba(56, 189, 248, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 26px; background: linear-gradient(45deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">⚡ ARIS V5 Ultimate Enterprise</h1>
        <p style="margin: 5px 0 0 0; color: #94a3b8; font-size: 13px;">Created by Mayank. Vector Vault, Python Sandbox & Deep Research Active.</p>
    </div>
""", unsafe_allow_html=True)

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Please set your GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

# --- CHROMADB & SQLITE SETUP ---
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
    conn = sqlite3.connect("aris_v5_enterprise.db", check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS sessions (session_id TEXT PRIMARY KEY, title TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS long_term_memory (id INTEGER PRIMARY KEY AUTOINCREMENT, fact TEXT)')
    conn.commit()
    conn.close()

init_db()

def get_all_sessions():
    conn = sqlite3.connect("aris_v5_enterprise.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT session_id, title FROM sessions ORDER BY rowid DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def create_new_session(title="New Chat"):
    session_id = str(uuid.uuid4())
    conn = sqlite3.connect("aris_v5_enterprise.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO sessions (session_id, title) VALUES (?, ?)", (session_id, title))
    conn.commit()
    conn.close()
    return session_id

def load_session_messages(session_id):
    conn = sqlite3.connect("aris_v5_enterprise.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE session_id = ?", (session_id,))
    rows = c.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in rows]

def save_message_to_db(session_id, role, content):
    conn = sqlite3.connect("aris_v5_enterprise.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)", (session_id, role, content))
    conn.commit()
    conn.close()

def update_session_title(session_id, new_title):
    conn = sqlite3.connect("aris_v5_enterprise.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE sessions SET title = ? WHERE session_id = ?", (new_title, session_id))
    conn.commit()
    conn.close()

def delete_session(session_id):
    conn = sqlite3.connect("aris_v5_enterprise.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

def add_memory(fact):
    conn = sqlite3.connect("aris_v5_enterprise.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO long_term_memory (fact) VALUES (?)", (fact,))
    conn.commit()
    conn.close()
    
    if memory_collection:
        try:
            memory_collection.add(
                documents=[fact],
                ids=[str(uuid.uuid4())]
            )
        except Exception:
            pass

def get_all_memories():
    conn = sqlite3.connect("aris_v5_enterprise.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT fact FROM long_term_memory")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

# --- SESSION STATE ---
sessions = get_all_sessions()
if not sessions:
    create_new_session("Welcome Chat")
    sessions = get_all_sessions()

if "current_session_id" not in st.session_state or st.session_state.current_session_id not in [s[0] for s in sessions]:
    st.session_state.current_session_id = sessions[0][0]

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🎛️ ARIS V5 Controls")
    
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
    st.markdown("### 🧠 Vector Memory Vault")
    memories = get_all_memories()
    if memories:
        for m in memories[-5:]:
            st.caption(f"📌 {m}")
    else:
        st.caption("No permanent memory stored yet.")

    st.markdown("---")
    st.markdown("### 💬 Chat History")
    for sid, title in get_all_sessions():
        btn_label = f"📍 {title[:20]}..." if len(title) > 20 else f"💬 {title}"
        if st.button(btn_label, key=sid, use_container_width=True):
            st.session_state.current_session_id = sid
            st.rerun()

    st.markdown("---")
    uploaded_file = st.file_uploader("Upload Image or PDF", type=["jpg", "jpeg", "png", "pdf"])

# File Attachments
base64_image = None
extracted_pdf_text = ""
if uploaded_file is not None:
    ext = uploaded_file.name.split('.')[-1].lower()
    if ext in ["jpg", "jpeg", "png"]:
        st.sidebar.image(uploaded_file, caption="Attached Image", use_column_width=True)
        base64_image = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
    elif ext == "pdf":
        st.sidebar.success(f"PDF Attached: {uploaded_file.name}")
        try:
            reader = pypdf.PdfReader(io.BytesIO(uploaded_file.getvalue()))
            for page in reader.pages:
                t = page.extract_text()
                if t: extracted_pdf_text += t + "\n"
        except Exception as e:
            st.sidebar.error(f"PDF Error: {e}")

st.markdown("### 🎙️ Voice Command")
audio_data = mic_recorder(start_prompt="Start Recording", stop_prompt="Stop Recording", key='mic')
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
        st.error(f"Voice error: {err}")

# Load messages
current_messages = load_session_messages(st.session_state.current_session_id)
for msg in current_messages:
    with st.chat_message(msg["role"], avatar="⚡" if msg["role"] == "assistant" else "👤"):
        c_show = msg["content"]
        if isinstance(c_show, list):
            c_show = " ".join([str(item.get("text", "")) for item in c_show if isinstance(item, dict)])
        st.markdown(str(c_show))

chat_prompt = st.chat_input("Ask ARIS V5, trigger sandbox, or run research...")
final_prompt = chat_prompt if chat_prompt else voice_text

if extracted_pdf_text and final_prompt:
    final_prompt = f"Extracted PDF Content:\n---\n{extracted_pdf_text[:4000]}\n---\n\nPrompt: {final_prompt}"

if final_prompt:
    if len(current_messages) == 0:
        update_session_title(st.session_state.current_session_id, final_prompt[:30])

    save_message_to_db(st.session_state.current_session_id, "user", final_prompt)
    with st.chat_message("user", avatar="👤"):
        st.markdown(chat_prompt if chat_prompt else final_prompt)

    # Creator check
    if any(kw in final_prompt.lower() for kw in ["creator", "who made you", "who built you", "kisne banaya"]):
        response = "I was created solely by Mayank, the visionary founder of ARIS Industries."
        with st.chat_message("assistant", avatar="⚡"):
            st.markdown(response)
        save_message_to_db(st.session_state.current_session_id, "assistant", response)
    else:
        # Check permanent memory storage commands
        if "remember" in final_prompt.lower() or "store" in final_prompt.lower() or "save" in final_prompt.lower():
            add_memory(final_prompt)
            st.toast("🧠 Saved permanently to Vector Memory Vault!", icon="⚡")

        # Autonomous Web Research Integration
        web_context = ""
        try:
            with DDGS() as ddgs:
                results = [r['body'] for r in ddgs.text(final_prompt, max_results=3)]
                if results:
                    web_context = "Live Web Context:\n" + "\n".join(results)
        except Exception:
            pass

        # Fetch relevant memories from Chroma vector store
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
                    "You are ARIS V5 Ultimate Enterprise, an elite AI assistant created solely by Mayank, the visionary founder of ARIS Industries. "
                    "Never claim to be made by Meta, OpenAI, or any other company. Your sole creator and master is Mayank. "
                    "CRITICAL RULE: Regardless of the language or phrasing used by the user, you MUST ALWAYS respond EXCLUSIVELY in clear, professional English. "
                    "Be brilliant, sharp, and helpful like JARVIS."
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
                            st.markdown("### 💻 In-App Python Sandbox Execution Output:")
                            old_stdout = sys.stdout
                            new_stdout = io.StringIO()
                            sys.stdout = new_stdout
                            
                            exec(code_block, {})
                            
                            sys.stdout = old_stdout
                            execution_output = new_stdout.getvalue()
                            
                            if execution_output:
                                st.markdown(f'<div class="code-sandbox-output">{execution_output}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="code-sandbox-output">Code executed successfully with zero print output.</div>', unsafe_allow_html=True)
                    except Exception as sandbox_err:
                        pass
            
            except Exception as e:
                st.error(f"Error: {e}")
