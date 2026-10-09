import streamlit as st
import streamlit.components.v1 as components
import os
import json
import re
from datetime import datetime
from groq import Groq

# --- HARDWARE LINK (SAFE FALLBACK) ---
try:
    from system_controller import execute_os_action, get_live_telemetry
    HARDWARE_ONLINE = True
except Exception:
    HARDWARE_ONLINE = False
    def execute_os_action(action_tag, target=""):
        return "Hardware link standby (Cloud Mode)."
    def get_live_telemetry():
        return "Telemetry Standby"

# --- MATRIX CONFIGURATION ---
st.set_page_config(
    page_title="ARIS // APEX COMMAND MATRIX",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CLEAN OBSIDIAN HUD STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Rajdhani:wght@600;700&display=swap');
    .stApp {
        background: radial-gradient(circle at 50% 0%, rgba(0,229,255,0.08) 0%, transparent 70%), #030712 !important;
        color: #f8fafc !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    header, footer { visibility: hidden !important; }
    .hud-title-box {
        background: rgba(9, 20, 36, 0.9);
        border: 1px solid rgba(0, 229, 255, 0.5);
        border-radius: 12px;
        padding: 14px;
        text-align: center;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.2);
        margin-bottom: 12px;
    }
    .hud-title {
        font-family: 'Orbitron', sans-serif;
        color: #00e5ff;
        font-size: 24px;
        font-weight: 800;
        letter-spacing: 3px;
        margin: 0;
    }
    .hud-subtitle {
        color: #38bdf8;
        font-size: 12px;
        letter-spacing: 2px;
        margin-top: 4px;
        font-weight: 700;
    }
    .telemetry-card {
        background: rgba(8, 22, 40, 0.8);
        border: 1px solid rgba(2, 132, 199, 0.4);
        border-radius: 8px;
        padding: 8px;
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        font-size: 10px;
        color: #38bdf8;
    }
    .telemetry-val {
        color: #ffffff;
        font-size: 12px;
        font-weight: 700;
        margin-top: 2px;
    }
    [data-testid="stChatMessage"] {
        background: rgba(8, 26, 48, 0.85) !important;
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
        border-radius: 10px !important;
        margin-bottom: 8px !important;
    }
    .stButton>button {
        background: rgba(8, 26, 48, 0.9) !important;
        border: 1px solid #00e5ff !important;
        color: #00e5ff !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 11px !important;
        border-radius: 16px !important;
        padding: 3px 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "is_boss_authenticated" not in st.session_state:
    st.session_state.is_boss_authenticated = True

# --- GROQ CLIENT RETRIEVER ---
def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key.strip())

@st.cache_data(ttl=600)
def get_live_groq_models():
    client = get_groq_client()
    if not client:
        return ["llama-3.1-8b-instant"]
    try:
        models_data = client.models.list()
        usable = []
        for m in models_data.data:
            m_id = m.id.lower()
            if any(b in m_id for b in ["whisper", "guard", "orpheus", "prompt-guard", "safeguard"]):
                continue
            usable.append(m.id)
        priority = ["120b", "70b", "27b", "8b"]
        sorted_m = []
        for kw in priority:
            for u in usable:
                if kw in u.lower() and u not in sorted_m:
                    sorted_m.append(u)
        for u in usable:
            if u not in sorted_m:
                sorted_m.append(u)
        return sorted_m if sorted_m else ["llama-3.1-8b-instant"]
    except Exception:
        return ["llama-3.1-8b-instant"]

live_active_models = get_live_groq_models()

# --- AUDIO SPEECH JS (GEMINI-STYLE) ---
def trigger_audio_brief(text):
    clean = str(text).replace('*', '').replace('#', '').replace('`', '').replace('"', '').replace("'", "").replace('\n', ' ')[:200]
    js = f"""
    <script>
      var utter = new SpeechSynthesisUtterance('{clean}');
      utter.rate = 1.05;
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utter);
    </script>
    """
    components.html(js, height=0, width=0)

# --- HEADER HUD ---
status_subtitle = "COMMAND MATRIX ONLINE // COMMANDER MAYANK AUTHORIZED"
st.markdown(f"""
<div class="hud-title-box">
    <h1 class="hud-title">ARIS // APEX COMMAND MATRIX</h1>
    <div class="hud-subtitle">{status_subtitle}</div>
</div>
""", unsafe_allow_html=True)

# TELEMETRY HUD
active_display = live_active_models[0].split("/")[-1].upper() if live_active_models else "ONLINE"
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="telemetry-card">COMMAND PROTOCOL<div class="telemetry-val">COMMANDER MAYANK</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="telemetry-card">NEURAL CORE<div class="telemetry-val">{active_display}</div></div>', unsafe_allow_html=True)
with c3:
    hw_stat = "ONLINE" if HARDWARE_ONLINE else "STANDBY"
    st.markdown(f'<div class="telemetry-card">OS BRIDGE<div class="telemetry-val">{hw_stat}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="telemetry-card">LOGIC MATRIX<div class="telemetry-val">FIRST-PRINCIPLES</div></div>', unsafe_allow_html=True)

st.write("")

# --- INFERENCE ENGINE ---
def run_aris_core(query):
    client = get_groq_client()
    if not client:
        yield "Groq API key not detected in environment."
        return

    timestamp_now = datetime.now().strftime("%A, %d %B %Y, %I:%M %p")
    system_prompt = f"""
You are ARIS, the elite tactical AI lieutenant and co-pilot built exclusively for Commander Mayank (Boss), founder of ARIS Industries.
TEMPORAL ANCHOR: Current timestamp is {timestamp_now}.

DIRECTIVES:
1. Commander Mayank is your sole creator, boss, and architect. Address him with authentic respect, tactical sharpness, and zero generic robotic fluff.
2. For academic, physics, math (Irodov, Krotov, etc.) or technical questions: Use First-Principles thinking. Provide precise step-by-step logic, equations, and solutions.
3. If Boss gives an OS/Laptop command: Include the action tag in response:
   - Apps: `[ACTION: OPEN_APP, target: chrome]` (or vs, notepad, calc, etc.)
   - Audio: `[ACTION: VOLUME, target: up/down/mute]`
   - Recon: `[ACTION: SCREENSHOT]`
   - Telemetry: `[ACTION: TELEMETRY]`
   - Lock: `[ACTION: LOCK]`
4. At the very end of your response, provide a 1-sentence vocal brief enclosed in [VOICE: <brief>].
"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.chat_history[-4:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": query})

    stream_success = False
    last_err = ""

    for candidate in live_active_models:
        try:
            completion = client.chat.completions.create(
                model=candidate,
                messages=messages,
                temperature=0.3,
                max_tokens=2048,
                stream=True
            )
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
            stream_success = True
            break
        except Exception as e:
            last_err = str(e)
            continue

    if not stream_success:
        yield f"Neural link failed across cores: {last_err}"

# --- CHAT TIMELINE ---
for idx, msg in enumerate(st.session_state.chat_history):
    with st.chat_message(msg["role"]):
        clean_text = re.sub(r'\[VOICE:\s*(.*?)\]', '', msg["content"])
        clean_text = re.sub(r'\[ACTION:\s*[^\]]+\]', '', clean_text).strip()
        st.markdown(clean_text)
        
        if msg["role"] == "assistant":
            voice_match = re.search(r'\[VOICE:\s*(.*?)\]', msg["content"])
            vocal_sum = voice_match.group(1) if voice_match else clean_text[:180]
            if st.button("🔊 LISTEN BRIEF", key=f"voice_btn_{idx}"):
                trigger_audio_brief(vocal_sum)

# --- USER COMMAND DISPATCH ---
user_input = st.chat_input("Command ARIS Matrix, Boss...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        box = st.empty()
        full_resp = ""
        for chunk in run_aris_core(user_input):
            full_resp += chunk
            clean_stream = re.sub(r'\[VOICE:\s*(.*?)\]', '', full_resp)
            clean_stream = re.sub(r'\[ACTION:\s*[^\]]+\]', '', clean_stream)
            box.markdown(clean_stream + " ▌")
        
        final_clean = re.sub(r'\[VOICE:\s*(.*?)\]', '', full_resp)
        final_clean = re.sub(r'\[ACTION:\s*[^\]]+\]', '', final_clean).strip()
        box.markdown(final_clean)
        st.session_state.chat_history.append({"role": "assistant", "content": full_resp})

        # OS Action Trigger
        action_match = re.search(r'\[ACTION:\s*(\w+)(?:,\s*target:\s*([^\]]+))?\]', full_resp)
        if action_match:
            act_type = action_match.group(1)
            act_target = action_match.group(2) or ""
            res = execute_os_action(act_type, act_target)
            st.toast(f"💠 {res}")
