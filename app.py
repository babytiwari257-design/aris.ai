import streamlit as st
import streamlit.components.v1 as components
import os
import time
import subprocess
from PIL import Image
from groq import Groq

# --- MATRIX HUD CONFIGURATION ---
st.set_page_config(
    page_title="ARIS Matrix Supreme",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CYBERPUNK HUD STYLES ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap');

    .stApp {
        background: radial-gradient(circle at 50% 20%, #03121e 0%, #010408 100%);
        color: #d1ecf1;
        font-family: 'Rajdhani', sans-serif;
    }
    [data-testid="stSidebar"] {
        background: rgba(2, 8, 16, 0.95);
        border-right: 1px solid rgba(0, 243, 255, 0.2);
    }
    .jarvis-header {
        background: linear-gradient(135deg, rgba(4, 30, 48, 0.9) 0%, rgba(2, 12, 24, 0.95) 100%);
        border: 1px solid #00f3ff;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 30px rgba(0, 243, 255, 0.25);
        margin-bottom: 20px;
    }
    .jarvis-title {
        font-family: 'Orbitron', sans-serif;
        color: #00f3ff;
        font-size: 26px;
        font-weight: 900;
        letter-spacing: 3px;
        margin: 0;
    }
    .jarvis-sub {
        color: #38bdf8;
        font-size: 13px;
        letter-spacing: 2px;
        margin-top: 5px;
    }
    .hud-card {
        background: rgba(4, 18, 30, 0.85);
        border: 1px solid rgba(0, 243, 255, 0.3);
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        font-size: 11px;
        color: #38bdf8;
    }
    .hud-val {
        color: #ffffff;
        font-size: 14px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if "threads" not in st.session_state:
    st.session_state.threads = {"Master Terminal": []}
if "current_thread" not in st.session_state:
    st.session_state.current_thread = "Master Terminal"
if "memory_vault" not in st.session_state:
    st.session_state.memory_vault = []
if "manual_groq_key" not in st.session_state:
    st.session_state.manual_groq_key = ""

# --- GROQ CLIENT RETRIEVER ---
def get_groq_client():
    # 1. Check user input in sidebar
    # 2. Check Streamlit Secrets
    # 3. Check environment variables
    api_key = (
        st.session_state.manual_groq_key
        or st.secrets.get("GROQ_API_KEY")
        or os.environ.get("GROQ_API_KEY")
    )
    if not api_key:
        return None
    return Groq(api_key=api_key.strip())

# --- DYNAMIC ACTIVE MODEL RESOLVER ---
@st.cache_data(ttl=1800)
def resolve_active_groq_model():
    client = get_groq_client()
    if not client:
        return "llama-3.3-70b-versatile"
    
    preferred_models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768"
    ]
    try:
        live_catalog = client.models.list()
        active_ids = [m.id for m in live_catalog.data if getattr(m, 'active', True)]
        for pref in preferred_models:
            if pref in active_ids:
                return pref
        for m_id in active_ids:
            if "whisper" not in m_id.lower() and "guard" not in m_id.lower():
                return m_id
    except Exception:
        pass
    return "llama-3.3-70b-versatile"

# --- PUHEAGENTTI (MJ VOICE AGENT) ---
def mj_voice_agent(text):
    try:
        clean_text = str(text).replace('"', '').replace("'", "").replace("\n", " ")
        if len(clean_text) > 200:
            clean_text = clean_text[:200] + " ... response continues on interface."
        js_code = f"""
        <script>
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance('{clean_text}');
                msg.rate = 1.05;
                window.speechSynthesis.speak(msg);
            }}
        </script>
        """
        components.html(js_code, height=0, width=0)
    except Exception:
        pass

# --- LOCAL DESKTOP AUTOMATION (OMEGA) ---
def omega_desktop_agent(query):
    try:
        q_lower = query.lower()
        if "open notepad" in q_lower:
            subprocess.Popen(["notepad.exe"])
            return "OMEGA: Notepad initiated on local system, Boss."
        elif "open chrome" in q_lower or "open browser" in q_lower:
            os.system("start chrome")
            return "OMEGA: Browser window launched successfully."
        elif "shutdown pc" in q_lower:
            os.system("shutdown /s /t 10")
            return "SECURITY WARNING: Shutdown sequence initiated (10s)."
    except Exception as e:
        return f"OMEGA Execution Error: {str(e)}"
    return None

# --- STREAMING CORE WITH RETRIES ---
def stream_groq_safe(client, model, messages, max_retries=2):
    for attempt in range(max_retries):
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.4,
                max_tokens=2500,
                stream=True
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
            return
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg and attempt < max_retries - 1:
                time.sleep(2)
            else:
                yield f"\n\n[GROQ EXECUTION FAULT]: {err_msg}"
                return

# --- MASTER CONTROLLER ---
def run_jarvis_core_stream(query, uploaded_file=None):
    client = get_groq_client()
    if not client:
        yield "SYSTEM ERROR: GROQ_API_KEY nahi mili! Sidebar me key daalein ya Streamlit Secrets me GROQ_API_KEY add karein."
        return

    q_lower = query.lower() if query else ""

    # Language Detection
    hindi_keywords = ["kya", "kaise", "batao", "likho", "hain", "hai", "kaun", "karo", "yeh", "woh", "mujhe", "mera"]
    is_hindi = any(word in q_lower for word in hindi_keywords) or any(ord(c) > 127 for c in query)

    # Memory Handler
    if q_lower.startswith("remember "):
        fact = query[9:].strip()
        if fact and fact not in st.session_state.memory_vault:
            st.session_state.memory_vault.append(fact)
        ack = f"ARIS: Memory updated: '{fact}', Boss." if is_hindi else f"ARIS: Neural vault registered: '{fact}', Sir."
        yield ack
        return

    # Desktop Ops
    desktop_res = omega_desktop_agent(query)
    if desktop_res:
        yield desktop_res
        return

    memories = "\n".join([f"- {m}" for m in st.session_state.memory_vault]) or "None."
    lang_directive = (
        "Respond in razor-sharp, loyal, conversational Hinglish (like Jarvis addressing Boss)."
        if is_hindi else
        "Respond in elite British Jarvis tone, addressing user as Boss or Sir."
    )

    system_prompt = f"""
You are ARIS // JARVIS-Supreme, an elite AI entity engineered by Mayank (Boss).
Tone: Razor-sharp intelligence, ultra-fast responses, loyal, witty.
{lang_directive}

[NEURAL MEMORY VAULT]:
{memories}
"""

    messages = [{"role": "system", "content": system_prompt}]
    
    # Thread Context
    thread_history = st.session_state.threads[st.session_state.current_thread]
    for msg in thread_history[-4:]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    final_query = query
    if uploaded_file is not None:
        final_query = f"[Diagnostic File Uploaded: {uploaded_file.name}] {query}"

    messages.append({"role": "user", "content": final_query})

    active_model = resolve_active_groq_model()
    for chunk in stream_groq_safe(client=client, model=active_model, messages=messages):
        yield chunk

# --- SIDEBAR CONTROL DECK ---
with st.sidebar:
    st.markdown("### 💠 ARIS COMMAND DECK")
    
    # Direct Key Input Fallback
    key_input = st.text_input(
        "🔑 Groq API Key (Optional Override)",
        type="password",
        value=st.session_state.manual_groq_key,
        help="Agar Secrets load na ho rahe hon toh direct yahan paste karein."
    )
    if key_input != st.session_state.manual_groq_key:
        st.session_state.manual_groq_key = key_input
        st.rerun()

    if st.button("🗑️ Purge Thread Memory", use_container_width=True):
        st.session_state.threads[st.session_state.current_thread] = []
        st.rerun()

    st.markdown("---")
    st.markdown("🧠 **Memory Vault**")
    if not st.session_state.memory_vault:
        st.caption("Empty. Use: `remember <fact>`")
    else:
        for idx, mem in enumerate(st.session_state.memory_vault):
            st.info(f"• {mem}")

active_model_name = resolve_active_groq_model()

# --- HEADER HUD ---
st.markdown(f"""
<div class="jarvis-header">
    <h1 class="jarvis-title">ARIS // JARVIS CORE</h1>
    <div class="jarvis-sub">ENGINE: GROQ LPU | ACTIVE MODEL: {active_model_name.upper()}</div>
</div>
""", unsafe_allow_html=True)

# Telemetry Cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="hud-card">STATUS<div class="hud-val">ONLINE 100%</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="hud-card">NEURAL CORE<div class="hud-val">{active_model_name.split("/")[-1].upper()}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="hud-card">MEMORY VAULT<div class="hud-val">{len(st.session_state.memory_vault)} ENTRIES</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="hud-card">LATENCY<div class="hud-val">&lt; 0.2 SEC</div></div>', unsafe_allow_html=True)

st.write("")

# Diagnostic image feed
uploaded_file = st.file_uploader("📤 Multimodal Optical Feed", type=["jpg", "jpeg", "png", "webp"])
if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Optical Target Acquired", width=280)

# Message History
current_messages = st.session_state.threads[st.session_state.current_thread]
for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
user_query = st.chat_input("Command Jarvis Core...")

if user_query:
    current_messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        stream_placeholder = st.empty()
        full_reply = ""

        for chunk in run_jarvis_core_stream(user_query, uploaded_file):
            full_reply += chunk
            stream_placeholder.markdown(full_reply + " ▌")

        stream_placeholder.markdown(full_reply)
        current_messages.append({"role": "assistant", "content": full_reply})
        mj_voice_agent(full_reply)
