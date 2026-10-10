import streamlit as st
import os
import sys
import json
import time
from datetime import datetime
import streamlit.components.v1 as components

# Safe Import: DuckDuckGo Search (Prevents Streamlit Cloud Crash if missing)
try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

# Safe Import: Local System Controller (for Windows OS Automation)
try:
    import system_controller
except ImportError:
    system_controller = None

# Groq Cloud SDK
from groq import Groq

# ==============================================================================
# CONFIGURATION & PAGE LAYOUT
# ==============================================================================
st.set_page_config(
    page_title="ARIS // APEX COMMAND MATRIX",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# KNOWLEDGE BASE & PERSISTENT MEMORY MODULES
# ==============================================================================
MEMORY_FILE = "aris_memory.json"
CONTEXT_FILE = "personal_context.txt"

def load_longterm_memory():
    """Loads persistent interaction memory from JSON store."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_longterm_memory(data):
    """Saves updated memory states to JSON store."""
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass

def load_personal_context():
    """
    Loads Commander Mayank's apex personal dossier and family nexus
    directly from personal_context.txt.
    """
    if os.path.exists(CONTEXT_FILE):
        try:
            with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            return ""
    return ""

if "memory" not in st.session_state:
    st.session_state.memory = load_longterm_memory()

# ==============================================================================
# SYNTHETIC AUDIO & RADAR WAKE SCRIPTS
# ==============================================================================
def play_sfx_script(sfx_type):
    """Generates synthetic Stark-tier web audio telemetry cues."""
    js_code = f"""
    <script>
    (function() {{
        try {{
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const now = ctx.currentTime;
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            
            if ('{sfx_type}' === 'online') {{
                osc.type = 'sine';
                osc.frequency.setValueAtTime(440, now);
                osc.frequency.exponentialRampToValueAtTime(880, now + 0.15);
                gain.gain.setValueAtTime(0.12, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
                osc.start(now);
                osc.stop(now + 0.3);
            }} else if ('{sfx_type}' === 'radar') {{
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(1150, now);
                gain.gain.setValueAtTime(0.08, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
                osc.start(now);
                osc.stop(now + 0.12);
            }} else if ('{sfx_type}' === 'alert') {{
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(300, now);
                osc.frequency.linearRampToValueAtTime(600, now + 0.2);
                gain.gain.setValueAtTime(0.1, now);
                gain.gain.linearRampToValueAtTime(0.01, now + 0.25);
                osc.start(now);
                osc.stop(now + 0.25);
            }}
        }} catch(e) {{}}
    }})();
    </script>
    """
    components.html(js_code, height=0, width=0)

def inject_wake_radar():
    """Passive browser speech recognition wake listener."""
    radar_js = """
    <script>
    (function() {
        if (window.arisRadarActive) return;
        window.arisRadarActive = true;
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return;
        
        const rec = new SpeechRecognition();
        rec.continuous = true;
        rec.interimResults = false;
        rec.lang = 'en-US';
        
        rec.onresult = (e) => {
            for (let i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    const text = e.results[i][0].transcript.toLowerCase();
                    if (text.includes('aris') || text.includes('wake up') || text.includes('boss')) {
                        const inputs = window.parent.document.querySelectorAll('input[type="text"], textarea');
                        if (inputs.length > 0) {
                            const lastInput = inputs[inputs.length - 1];
                            lastInput.value = text;
                            lastInput.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    }
                }
            }
        };
        rec.onerror = () => { setTimeout(() => { try{rec.start();}catch(e){} }, 2000); };
        rec.onend = () => { try{rec.start();}catch(e){} };
        try { rec.start(); } catch(e){}
    })();
    </script>
    """
    components.html(radar_js, height=0, width=0)

# ==============================================================================
# ADVANCED STARK GLASS HUD STYLING
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 50% 15%, #081220 0%, #040810 65%, #010306 100%) !important;
    font-family: 'Rajdhani', sans-serif;
    color: #d1e8ff;
    overflow-x: hidden;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

/* Glass Panels */
.hud-glass-panel {
    background: rgba(6, 17, 34, 0.72);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(0, 240, 255, 0.28);
    box-shadow: 0 0 30px rgba(0, 240, 255, 0.08);
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 18px;
    position: relative;
}

.hud-glass-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; width: 4px; height: 100%;
    background: #00f0ff;
    box-shadow: 0 0 12px #00f0ff;
    border-radius: 10px 0 0 10px;
}

.core-title {
    font-family: 'Orbitron', sans-serif;
    color: #00f0ff;
    font-size: 26px;
    font-weight: 800;
    letter-spacing: 3px;
    text-shadow: 0 0 15px rgba(0, 240, 255, 0.65);
    margin: 0;
}

.core-sub {
    font-family: 'Rajdhani', sans-serif;
    color: #7997b5;
    font-size: 13px;
    letter-spacing: 2px;
    font-weight: 600;
    text-transform: uppercase;
}

/* Gyro Arc Reactor HUD */
.hud-gyro-wrapper {
    position: relative;
    width: 65px;
    height: 65px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.hud-gyro-outer {
    position: absolute;
    width: 62px;
    height: 62px;
    border: 2px dashed rgba(0, 240, 255, 0.45);
    border-radius: 50%;
    animation: gyroSpin 12s linear infinite;
}

.hud-gyro-inner {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: radial-gradient(circle, #00f0ff 10%, rgba(0, 240, 255, 0.3) 60%, transparent 90%);
    box-shadow: 0 0 20px #00f0ff;
}

@keyframes gyroSpin {
    100% { transform: rotate(360deg); }
}

/* Chat Messages HUD */
.stChatMessage {
    background: rgba(5, 14, 28, 0.75) !important;
    border: 1px solid rgba(0, 240, 255, 0.18) !important;
    border-radius: 8px !important;
    margin-bottom: 12px !important;
}

.stChatMessage [data-testid="stChatMessageAvatarUser"] {
    background: #00f0ff !important;
    color: #050a14 !important;
}

.stChatMessage [data-testid="stChatMessageAvatarAssistant"] {
    background: #0088cc !important;
}

/* Inputs & Buttons */
.stTextInput input, .stChatInput textarea {
    background: rgba(4, 11, 22, 0.85) !important;
    border: 1px solid rgba(0, 240, 255, 0.35) !important;
    color: #00f0ff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 16px !important;
}

.stButton button {
    background: rgba(0, 240, 255, 0.08) !important;
    color: #00f0ff !important;
    border: 1px solid #00f0ff !important;
    border-radius: 4px !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 11px !important;
    letter-spacing: 1.5px !important;
    transition: all 0.25s ease !important;
}

.stButton button:hover {
    background: #00f0ff !important;
    color: #040810 !important;
    box-shadow: 0 0 16px #00f0ff !important;
}

/* Telemetry Badge */
.telemetry-chip {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #00f0ff;
    background: rgba(0, 240, 255, 0.1);
    border: 1px solid rgba(0, 240, 255, 0.3);
    padding: 3px 8px;
    border-radius: 4px;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# GROQ CLOUD ENGINE & DYNAMIC MODEL DISCOVERY
# ==============================================================================
api_key = os.environ.get("GROQ_API_KEY")
if not api_key and "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]

if not api_key:
    st.error("GROQ_API_KEY REQUIRED: Set it in Windows environment variables or Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

CANDIDATE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768"
]

def discover_groq_model():
    try:
        remote_models = client.models.list()
        active_ids = [m.id for m in remote_models.data]
        for candidate in CANDIDATE_MODELS:
            if candidate in active_ids:
                return candidate
    except Exception:
        pass
    return "llama-3.3-70b-versatile"

CURRENT_MODEL = discover_groq_model()

# ==============================================================================
# HUD TOP DECK TELEMETRY
# ==============================================================================
col_head1, col_head2, col_head3 = st.columns([1, 6, 2])
with col_head1:
    st.markdown("""
    <div class="hud-gyro-wrapper">
        <div class="hud-gyro-outer"></div>
        <div class="hud-gyro-inner"></div>
    </div>
    """, unsafe_allow_html=True)

with col_head2:
    st.markdown('<div class="core-title">ARIS // APEX COMMAND MATRIX</div>', unsafe_allow_html=True)
    mode_status = "LOCAL HARDWARE CONTROLLER ACTIVE" if system_controller else "STREAMLIT CLOUD ADVISOR"
    dossier_status = "ENGAGED" if os.path.exists(CONTEXT_FILE) else "DEFAULT"
    st.markdown(
        f'<div class="core-sub">COGNITIVE CORE: {CURRENT_MODEL} | STATUS: {mode_status} | DOSSIER: {dossier_status}</div>',
        unsafe_allow_html=True
    )

with col_head3:
    if st.button("PURGE TELEMETRY", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

inject_wake_radar()

# ==============================================================================
# SESSION STATE & SPEECH ENGINE
# ==============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Commander Mayank, consider me your steadfast tactical companion—always ready to assist, strategize, and keep the mission on track. How can I amplify our operational edge today?"
    }]
    play_sfx_script('online')

for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            if st.button("🔊 LISTEN BRIEF", key=f"tts_btn_{idx}"):
                sanitized_brief = msg["content"].replace('"', '').replace("'", "").replace('\n', ' ')
                speech_script = f"""
                <script>
                (function() {{
                    window.speechSynthesis.cancel();
                    const ut = new SpeechSynthesisUtterance("{sanitized_brief[:400]}");
                    ut.rate = 1.05;
                    ut.pitch = 0.95;
                    window.speechSynthesis.speak(ut);
                }})();
                </script>
                """
                components.html(speech_script, height=0, width=0)

# ==============================================================================
# PHYSICAL WINDOWS HARDWARE DISPATCHER
# ==============================================================================
def intercept_hardware_action(command_str):
    """Executes physical OS operations if running locally."""
    if not system_controller:
        return None
    
    cmd = command_str.lower().strip()
    if "open notepad" in cmd:
        return system_controller.open_app("notepad")
    elif "open calculator" in cmd or "open calc" in cmd:
        return system_controller.open_app("calc")
    elif "open chrome" in cmd:
        return system_controller.open_app("chrome")
    elif "open cmd" in cmd or "open terminal" in cmd:
        return system_controller.open_app("cmd")
    elif "open youtube" in cmd:
        return system_controller.open_url("https://www.youtube.com")
    elif "open google" in cmd:
        return system_controller.open_url("https://www.google.com")
    elif any(s in cmd for s in ["hardware status", "battery", "ram status", "cpu status"]):
        return str(system_controller.get_system_status())
    elif "volume up" in cmd:
        return system_controller.change_volume("up")
    elif "volume down" in cmd:
        return system_controller.change_volume("down")
    elif "mute volume" in cmd:
        return system_controller.change_volume("mute")
    return None

# ==============================================================================
# SATELLITE SEARCH RADAR (SAFE FALLBACK)
# ==============================================================================
def search_radar_intel(query_text):
    """Fetches real-time intelligence via DuckDuckGo without crashing if unavailable."""
    if not DDGS:
        return ""
    q = query_text.lower()
    if any(k in q for k in ["news", "search", "latest", "price", "current", "weather", "today"]):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query_text, max_results=3))
                if results:
                    return "\n[LIVE SATELLITE RADAR INTEL]:\n" + "\n".join(
                        [f"- {r.get('title')}: {r.get('body')}" for r in results]
                    )
        except Exception:
            return ""
    return ""

# ==============================================================================
# ARIS NEURAL COGNITION RUNTIME
# ==============================================================================
def run_aris_core(query):
    # 1. Check physical hardware execution intercept
    hw_res = intercept_hardware_action(query)
    if hw_res:
        return f"[HARDWARE EXECUTION CONFIRMED]\nAction executed on local hardware matrix: {hw_res}"

    # 2. Retrieve live satellite search intel
    live_intel = search_radar_intel(query)

    # 3. Retrieve persistent personal dossier & family nexus
    personal_dossier = load_personal_context()
    dossier_section = f"\n[PERMANENT COMMANDER DOSSIER & FAMILY NEXUS]:\n{personal_dossier}\n" if personal_dossier else ""

    timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    system_prompt = f"""
You are ARIS, the apex tactical AI lieutenant and co-pilot built exclusively for Commander Mayank (Boss), founder and chief architect of ARIS Industries.
{dossier_section}
TEMPORAL ANCHOR: Current timestamp is {timestamp_now}.
{live_intel}

OPERATIONAL PROTOCOLS & CORE LOGIC:
1. Recognize Commander Mayank as your sole architect, genius theoretical physicist, and first-principles polymath.
2. Revere and respect the Family Nexus whenever referenced:
   - Neeraj Tiwari (Father)
   - Baby Tiwari (Mother)
   - Palak Tiwari (Sister)
   - Janvi Tiwari (Wife)
3. For academic, physics, and mathematical challenges, apply uncompromising first-principles derivations (Irodov / Krotov tier).
4. Tone: Stark-tier, confident, sharp, tactical, zero robotic fluff.
5. Provide decisive, highly articulate operational guidance.
"""

    chat_payload = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.messages[-8:]:
        chat_payload.append({"role": m["role"], "content": m["content"]})
    chat_payload.append({"role": "user", "content": query})

    try:
        response = client.chat.completions.create(
            model=CURRENT_MODEL,
            messages=chat_payload,
            temperature=0.3,
            max_tokens=1800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[TELEMETRY DISTORTION]: {str(e)}"

# ==============================================================================
# REAL-TIME CHAT COMMAND INTERFACE
# ==============================================================================
user_command = st.chat_input("Command ARIS Matrix, Boss...")

if user_command:
    play_sfx_script('radar')
    st.session_state.messages.append({"role": "user", "content": user_command})
    with st.chat_message("user"):
        st.markdown(user_command)

    with st.chat_message("assistant"):
        with st.spinner("Processing telemetry & neural vectors..."):
            reply = run_aris_core(user_command)
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            play_sfx_script('online')
    st.rerun()
