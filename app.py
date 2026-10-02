import streamlit as st
import os
import time
import subprocess
from PIL import Image
from google import genai
from google.genai import types
from google.genai.errors import APIError

# --- SIVUN KONFIGURAATIO / MATRIX CONFIG ---
st.set_page_config(
    page_title="ARIS  Matrix Supreme",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CYBERPUNK / JARVIS HUD TYYLIT ---
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
        box-shadow: 4px 0 25px rgba(0, 243, 255, 0.05);
    }

    .jarvis-header {
        background: linear-gradient(135deg, rgba(4, 30, 48, 0.9) 0%, rgba(2, 12, 24, 0.95) 100%);
        border: 1px solid #00f3ff;
        border-radius: 12px;
        padding: 24px 20px;
        text-align: center;
        box-shadow: 0 0 35px rgba(0, 243, 255, 0.25), inset 0 0 15px rgba(0, 243, 255, 0.1);
        margin-bottom: 25px;
    }
    .jarvis-title {
        font-family: 'Orbitron', sans-serif;
        color: #00f3ff;
        font-size: 26px;
        font-weight: 900;
        letter-spacing: 3px;
        text-shadow: 0 0 12px rgba(0, 243, 255, 0.8);
        margin: 0;
    }
    .jarvis-sub {
        color: #38bdf8;
        font-size: 13px;
        letter-spacing: 2px;
        margin-top: 5px;
        text-transform: uppercase;
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
        box-shadow: inset 0 0 10px rgba(0, 243, 255, 0.15);
    }
    .hud-val {
        color: #ffffff;
        font-size: 14px;
        font-weight: bold;
        text-shadow: 0 0 8px rgba(0, 243, 255, 0.8);
    }

    [data-testid="stChatMessage"]:nth-child(even) {
        background: rgba(3, 22, 33, 0.8) !important;
        border: 1px solid #00f3ff !important;
        border-radius: 12px;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.15);
        font-size: 16px;
    }
    [data-testid="stChatMessage"]:nth-child(even) p,
    [data-testid="stChatMessage"]:nth-child(even) li,
    [data-testid="stChatMessage"]:nth-child(even) span {
        color: #e0f7fa !important;
    }

    [data-testid="stChatMessage"]:nth-child(odd) {
        background: rgba(10, 31, 56, 0.7) !important;
        border: 1px solid #0284c7 !important;
        border-radius: 12px;
        font-size: 16px;
    }
    [data-testid="stChatMessage"]:nth-child(odd) p,
    [data-testid="stChatMessage"]:nth-child(odd) span {
        color: #38bdf8 !important;
        font-weight: 600;
    }

    .stTextInput input, .stTextArea textarea {
        background-color: #030d17 !important;
        border: 1px solid #00f3ff !important;
        color: #00f3ff !important;
    }
    .stButton button {
        background: linear-gradient(90deg, #0284c7 0%, #00f3ff 100%) !important;
        color: #010408 !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- GEMINI CLIENT (STRICTLY FROM SECRETS / ENV - NO HARDCODED KEY) ---
@st.cache_resource
def get_gemini_client():
    api_key = None
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    elif "GEMINI_API_KEY" in os.environ:
        api_key = os.environ["GEMINI_API_KEY"]

    if not api_key:
        return None
    return genai.Client(api_key=api_key)

# --- SESSION STATES ---
if "threads" not in st.session_state:
    st.session_state.threads = {"Master Terminal": []}
if "current_thread" not in st.session_state:
    st.session_state.current_thread = "Master Terminal"
if "memory_vault" not in st.session_state:
    st.session_state.memory_vault = []

# --- PUHEAGENTTI (MJ VOICE) ---
def mj_voice_agent(text):
    try:
        clean_text = str(text).replace('"', '').replace("'", "").replace("\n", " ")
        if len(clean_text) > 240:
            clean_text = clean_text[:240] + " ... response continues on interface."
        js_code = f"""
        <script>
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance('{clean_text}');
                msg.rate = 1.05;
                msg.pitch = 0.95;
                window.speechSynthesis.speak(msg);
            }}
        </script>
        """
        st.components.v1.html(js_code, height=0, width=0)
    except Exception:
        pass

# --- LOCAL DESKTOP AUTOMATION (OMEGA) ---
def omega_desktop_agent(query):
    try:
        q_lower = query.lower()
        if "open notepad" in q_lower:
            subprocess.Popen(["notepad.exe"])
            return "OMEGA: Notepad successfully launched on your system, Boss."
        elif "open chrome" in q_lower or "open browser" in q_lower:
            os.system("start chrome")
            return "OMEGA: Web browser initiated successfully."
        elif "shutdown pc" in q_lower:
            os.system("shutdown /s /t 10")
            return "SECURITY WARNING: System shutdown sequence armed for 10 seconds."
    except Exception as e:
        return f"OMEGA Execution Error: {str(e)}"
    return None

# --- SAFE RETRY STREAMING CORE (PREVENTS 429 CRASHES) ---
def stream_gemini_safe(client, model, contents, config, max_retries=3):
    for attempt in range(max_retries):
        try:
            stream = client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=config
            )
            for chunk in stream:
                if chunk.text:
                    yield chunk.text
            return
        except APIError as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = 2 ** (attempt + 1)
                time.sleep(wait_time)
            else:
                yield f"\n\n[API ALERT]: Rate limit hit or service error: {str(e)}"
                return
        except Exception as e:
            yield f"\n\n[CORE ERROR]: {str(e)}"
            return

# --- MASTER CONTROLLER (ARIS / JARVIS) ---
def run_jarvis_core_stream(query, uploaded_file=None):
    client = get_gemini_client()
    if not client:
        yield "SYSTEM ERROR: GEMINI_API_KEY nahi mili! Streamlit Cloud ke Settings -> Secrets me GEMINI_API_KEY daalein."
        return

    q_lower = query.lower() if query else ""

    # Detect Hindi/Hinglish
    hindi_keywords = ["kya", "kaise", "batao", "likho", "hain", "hai", "kaun", "karo", "yeh", "woh", "mujhe", "mera", "dekho"]
    is_hindi = any(word in q_lower for word in hindi_keywords) or any(ord(c) > 127 for c in query)

    # Memory Persistence
    if q_lower.startswith("remember "):
        fact = query[9:].strip()
        if fact and fact not in st.session_state.memory_vault:
            st.session_state.memory_vault.append(fact)
        ack = (
            f"ARIS (Jarvis Core): Fact stored in the neural memory vault: '{fact}'."
            if not is_hindi else
            f"ARIS: Memory vault me yeh fact secure ho chuka hai, Boss: '{fact}'."
        )
        yield ack
        return

    # Desktop Ops
    desktop_cmd = omega_desktop_agent(query)
    if desktop_cmd:
        yield desktop_cmd
        return

    # Directives
    lang_directive = (
        "User is communicating in Hindi/Hinglish. Respond in smart, witty, respectful Hinglish like Jarvis speaking with Boss."
        if is_hindi else
        "User is communicating in English. Speak in a sharp, articulate, high-IQ British Jarvis tone, addressing the user as Boss or Sir."
    )

    memories = st.session_state.get("memory_vault", [])
    memory_context = "\n".join([f"- {m}" for m in memories]) if memories else "No explicit records yet."

    system_prompt = f"""
You are ARIS // JARVIS-Supreme, an elite AI entity engineered by Mayank.
Your faculties:
- Multi-dimensional Reasoning & Strategic Architecture
- Software Engineering & Code Optimizations (Alpha Unit)
- Visual Perception & Diagnostic Telemetry (Omega Vision)
- Tactical Memory Vault Access (Helios)

Tone & Style: Confident, fast, razor-sharp intelligence, sophisticated, polite, and loyal to Boss.
{lang_directive}

[NEURAL MEMORY VAULT]:
{memory_context}
"""

    content_parts = []
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        mime_type = uploaded_file.type or "image/jpeg"
        content_parts.append(types.Part.from_bytes(data=bytes_data, mime_type=mime_type))

    content_parts.append(query)

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.4,
        max_output_tokens=3000
    )

    for chunk in stream_gemini_safe(
        client=client,
        model="gemini-2.5-flash",
        contents=content_parts,
        config=config,
        max_retries=3
    ):
        yield chunk

# --- SIDEBAR CONTROL DECK ---
with st.sidebar:
    st.markdown("### 💠 ARIS COMMAND DECK")

    new_thread = st.text_input("New Protocol", placeholder="Project Obsidian...")
    if st.button("⚡ Initialize Neural Thread", use_container_width=True):
        if new_thread and new_thread not in st.session_state.threads:
            st.session_state.threads[new_thread] = []
            st.session_state.current_thread = new_thread
            st.rerun()

    if st.button("🗑️ Purge Thread Memory", use_container_width=True):
        st.session_state.threads[st.session_state.current_thread] = []
        st.rerun()

    st.markdown("---")
    st.markdown("📡 **Active Data Streams**")
    for t_name in list(st.session_state.threads.keys()):
        active_marker = "🟢" if t_name == st.session_state.current_thread else "⚪"
        if st.button(f"{active_marker} {t_name}", use_container_width=True, key=f"th_{t_name}"):
            st.session_state.current_thread = t_name
            st.rerun()

    st.markdown("---")
    st.markdown("🧠 **Neural Memory Vault**")
    if not st.session_state.memory_vault:
        st.caption("Vault empty. Command 'remember <fact>' to persist.")
    else:
        for idx, mem in enumerate(st.session_state.memory_vault):
            col_m, col_d = st.columns([5, 1])
            with col_m:
                st.info(f"🔹 {mem}")
            with col_d:
                if st.button("✖", key=f"del_mem_{idx}"):
                    st.session_state.memory_vault.pop(idx)
                    st.rerun()

# --- MAIN INTERFACE HUD ---
st.markdown(f"""
<div class="jarvis-header">
    <h1 class="jarvis-title">ARIS // JARVIS CORE</h1>
    <div class="jarvis-sub">TACTICAL AI MATRIX | GEMINI 2.5 FLASH | STREAM: {st.session_state.current_thread}</div>
</div>
""", unsafe_allow_html=True)

# Telemetry cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="hud-card">STATUS<div class="hud-val">ONLINE 100%</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="hud-card">NEURAL CORE<div class="hud-val">GEMINI 2.5</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="hud-card">MEMORY VAULT<div class="hud-val">{len(st.session_state.memory_vault)} ENTRIES</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="hud-card">TELEMETRY<div class="hud-val">STREAM ACTIVE</div></div>', unsafe_allow_html=True)

st.write("")

# Diagnostic image upload
uploaded_file = st.file_uploader("📤 Multimodal Visual Feed (OCR / Target Inspection)", type=["jpg", "jpeg", "png", "webp"])
if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Optical Sensor Input Locked", width=320)

# Message timeline
current_messages = st.session_state.threads[st.session_state.current_thread]
for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Command Input
user_query = st.chat_input("Command Jarvis Core...")

if user_query or (uploaded_file and len(current_messages) == 0):
    query_text = user_query if user_query else "Diagnostic scan: Analyze this optical feed and report."

    current_messages.append({"role": "user", "content": query_text})
    with st.chat_message("user"):
        st.markdown(query_text)

    with st.chat_message("assistant"):
        stream_placeholder = st.empty()
        full_reply = ""

        # Real-time Stream with Safe Retries
        for chunk in run_jarvis_core_stream(query_text, uploaded_file):
            full_reply += chunk
            stream_placeholder.markdown(full_reply + " ▌")

        stream_placeholder.markdown(full_reply)
        current_messages.append({"role": "assistant", "content": full_reply})

        mj_voice_agent(full_reply)
