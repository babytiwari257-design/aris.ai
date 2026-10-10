import streamlit as st
import os
import sys
import json
import time
from datetime import datetime
import streamlit.components.v1 as components

# Safe Import: DuckDuckGo Search
try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

# Safe Import: Local System Controller
try:
    import system_controller
except ImportError:
    system_controller = None

from groq import Groq

# ==============================================================================
# MATRIX INITIALIZATION
# ==============================================================================
st.set_page_config(
    page_title="ARIS INDUSTRIES // APEX COMMAND HUD",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# PERSISTENT STORAGE & PERMANENT DOSSIER CORE
# ==============================================================================
MEMORY_FILE = "aris_memory.json"
CONTEXT_FILE = "personal_context.txt"

def load_longterm_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_longterm_memory(data):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass

def load_personal_context():
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
# ULTIMATE NEON GLOW STARK HUD & PURE CODE 'A' ARC-REACTOR CSS
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Share+Tech+Mono&family=Rajdhani:wght@500;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 50% 18%, #081a30 0%, #030a16 55%, #01040a 100%) !important;
    font-family: 'Rajdhani', sans-serif;
    color: #d8f0ff;
    overflow-x: hidden;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

/* Cyber Matrix Background Grid */
[data-testid="stAppViewContainer"]::before {
    content: " ";
    position: fixed;
    top: 0; left: 0; bottom: 0; right: 0;
    background: 
        linear-gradient(rgba(0, 240, 255, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 240, 255, 0.04) 1px, transparent 1px);
    background-size: 32px 32px;
    pointer-events: none;
    z-index: 0;
}

/* Center Stage Arc Reactor & Crest Deck */
.center-hud-deck {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-top: 10px;
    margin-bottom: 25px;
    text-align: center;
}

.arc-reactor-core-frame {
    position: relative;
    width: 170px;
    height: 170px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 12px;
}

.arc-spin-ring-outer {
    position: absolute;
    width: 166px;
    height: 166px;
    border-radius: 50%;
    border: 2px dashed #00ffa3;
    box-shadow: 0 0 25px rgba(0, 255, 163, 0.45);
    animation: spinClockwise 12s linear infinite;
}

.arc-spin-ring-inner {
    position: absolute;
    width: 148px;
    height: 148px;
    border-radius: 50%;
    border: 2px solid #00f0ff;
    box-shadow: 0 0 35px rgba(0, 240, 255, 0.6), inset 0 0 25px rgba(0, 240, 255, 0.35);
    animation: spinCounter 8s linear infinite;
}

/* Pure SVG Metallic 'A' Crest Emblem */
.crest-svg-container {
    width: 125px;
    height: 125px;
    z-index: 2;
    filter: drop-shadow(0 0 16px rgba(0, 240, 255, 0.85)) drop-shadow(0 0 30px rgba(0, 255, 163, 0.4));
    animation: emblemPulse 2.5s ease-in-out infinite alternate;
}

@keyframes spinClockwise {
    100% { transform: rotate(360deg); }
}

@keyframes spinCounter {
    100% { transform: rotate(-360deg); }
}

@keyframes emblemPulse {
    0% { transform: scale(0.96); filter: drop-shadow(0 0 14px rgba(0, 240, 255, 0.7)); }
    100% { transform: scale(1.04); filter: drop-shadow(0 0 24px rgba(0, 240, 255, 1)) drop-shadow(0 0 36px rgba(0, 255, 163, 0.6)); }
}

.aris-title-text {
    font-family: 'Orbitron', sans-serif;
    color: #00f0ff;
    font-size: 34px;
    font-weight: 900;
    letter-spacing: 6px;
    text-shadow: 0 0 20px rgba(0, 240, 255, 0.9), 0 0 40px rgba(0, 240, 255, 0.4);
    margin: 4px 0;
}

.aris-sub-text {
    font-family: 'Share Tech Mono', monospace;
    color: #00ffa3;
    font-size: 13px;
    letter-spacing: 4px;
    text-transform: uppercase;
    text-shadow: 0 0 10px rgba(0, 255, 163, 0.5);
    margin-bottom: 15px;
}

/* Telemetry Badges */
.telemetry-row {
    display: flex;
    justify-content: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 10px;
}

.telemetry-badge {
    background: rgba(0, 240, 255, 0.08);
    border: 1px solid rgba(0, 240, 255, 0.4);
    padding: 5px 16px;
    border-radius: 4px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #7be9ff;
    letter-spacing: 1.5px;
    box-shadow: 0 0 12px rgba(0, 240, 255, 0.15);
}

/* Chat Styling */
.stChatMessage {
    background: rgba(4, 14, 28, 0.88) !important;
    border: 1px solid rgba(0, 240, 255, 0.25) !important;
    border-left: 5px solid #00f0ff !important;
    border-radius: 6px !important;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.6) !important;
    margin-bottom: 16px !important;
}

.stButton button {
    background: linear-gradient(135deg, rgba(0, 240, 255, 0.18) 0%, rgba(0, 255, 163, 0.1) 100%) !important;
    color: #00f0ff !important;
    border: 1px solid #00f0ff !important;
    border-radius: 4px !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    transition: all 0.25s ease !important;
}

.stButton button:hover {
    background: #00f0ff !important;
    color: #01050e !important;
    box-shadow: 0 0 25px #00f0ff, 0 0 45px rgba(0, 240, 255, 0.6) !important;
}

.stChatInput textarea, .stTextInput input {
    background: rgba(3, 9, 20, 0.95) !important;
    border: 1px solid rgba(0, 240, 255, 0.45) !important;
    color: #00f0ff !important;
    font-family: 'Share Tech Mono', monospace !important;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# AUDIO SFX & RADAR SCRIPT
# ==============================================================================
def play_sfx_script(sfx_type):
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
                osc.frequency.setValueAtTime(350, now);
                osc.frequency.exponentialRampToValueAtTime(900, now + 0.2);
                gain.gain.setValueAtTime(0.18, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.38);
                osc.start(now);
                osc.stop(now + 0.38);
            }} else if ('{sfx_type}' === 'radar') {{
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(1350, now);
                gain.gain.setValueAtTime(0.1, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.14);
                osc.start(now);
                osc.stop(now + 0.14);
            }}
        }} catch(e) {{}}
    }})();
    </script>
    """
    components.html(js_code, height=0, width=0)

def inject_wake_radar():
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
# GROQ CLIENT SETUP
# ==============================================================================
api_key = os.environ.get("GROQ_API_KEY")
if not api_key and "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]

if not api_key:
    st.error("SYSTEM ERROR: GROQ_API_KEY nahi mili! Streamlit Cloud ke Settings -> Secrets me GROQ_API_KEY daalein.")
    st.stop()

client = Groq(api_key=api_key)

FALLBACK_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768"
]

def query_groq_resilient(chat_payload):
    last_err = None
    for model_name in FALLBACK_MODELS:
        try:
            res = client.chat.completions.create(
                model=model_name,
                messages=chat_payload,
                temperature=0.3,
                max_tokens=1800
            )
            return res.choices[0].message.content
        except Exception as err:
            err_str = str(err).lower()
            if "404" in err_str or "model_not_found" in err_str or "does not exist" in err_str:
                last_err = err
                continue
            raise err
    return f"[TELEMETRY DISTORTION]: {str(last_err)}"

# ==============================================================================
# PURE CODE: SVG METALLIC 'A' + ARC REACTOR CENTER STAGE
# ==============================================================================
metallic_a_svg = """
<svg class="crest-svg-container" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="metalGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#b8d5e5" />
      <stop offset="25%" stop-color="#6a8ca8" />
      <stop offset="50%" stop-color="#2c4c66" />
      <stop offset="75%" stop-color="#739bb8" />
      <stop offset="100%" stop-color="#e2f1fa" />
    </linearGradient>
    <linearGradient id="neonCyan" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00ffa3" />
      <stop offset="100%" stop-color="#00f0ff" />
    </linearGradient>
    <filter id="neonGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>
  
  <!-- Outer Hexagonal Frame Layer -->
  <polygon points="100,22 165,58 165,138 100,178 35,138 35,58" stroke="url(#metalGrad)" stroke-width="4.5" fill="none" opacity="0.85" />
  <polygon points="100,28 158,62 158,134 100,170 42,134 42,62" stroke="url(#neonCyan)" stroke-width="2" fill="none" opacity="0.6" filter="url(#neonGlow)" />
  
  <!-- The Iconic Metallic Geometric 'A' Crest -->
  <path d="M 100,38 L 148,145 L 126,145 L 115,120 L 85,120 L 74,145 L 52,145 Z" fill="url(#metalGrad)" stroke="#00f0ff" stroke-width="2" />
  
  <!-- Inner Cutout -->
  <polygon points="100,68 110,104 90,104" fill="#040d1a" stroke="url(#neonCyan)" stroke-width="2" />
  
  <!-- Circuit Neon Trace Accents inside 'A' -->
  <path d="M 100,45 L 138,135" stroke="#00f0ff" stroke-width="2.5" stroke-linecap="round" filter="url(#neonGlow)" />
  <circle cx="138" cy="135" r="3" fill="#00ffa3" filter="url(#neonGlow)" />
  <path d="M 75,135 L 90,105" stroke="#00ffa3" stroke-width="2" stroke-linecap="round" filter="url(#neonGlow)" />
  <circle cx="75" cy="135" r="2.5" fill="#00f0ff" filter="url(#neonGlow)" />
  
  <!-- Horizontal Core Power Bar -->
  <line x1="80" y1="112" x2="120" y2="112" stroke="#00ffa3" stroke-width="3" filter="url(#neonGlow)" />
</svg>
"""

hw_status = "ONLINE" if system_controller else "STANDBY"
dossier_status = "SYNCHRONIZED" if os.path.exists(CONTEXT_FILE) else "DEFAULT"

st.markdown(f"""
<div class="center-hud-deck">
    <div class="arc-reactor-core-frame">
        <div class="arc-spin-ring-outer"></div>
        <div class="arc-spin-ring-inner"></div>
        {metallic_a_svg}
    </div>
    <div class="aris-title-text">ARIS INDUSTRIES</div>
    <div class="aris-sub-text">AUTONOMOUS RECONNAISSANCE & INTELLIGENCE SYSTEM // APEX CORE</div>
    <div class="telemetry-row">
        <span class="telemetry-badge">COMMANDER: MAYANK TIWARI (BOSS)</span>
        <span class="telemetry-badge">COGNITIVE ENGINE: LLAMA-3.3-70B AUTO</span>
        <span class="telemetry-badge">HARDWARE CONTROL: {hw_status}</span>
        <span class="telemetry-badge">DOSSIER: {dossier_status}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Top Bar Control
col_space, col_purge = st.columns([8, 2])
with col_purge:
    if st.button("PURGE BUFFER", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

inject_wake_radar()

# ==============================================================================
# CHAT LOGS
# ==============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Commander Mayank, ARIS Industries Tactical Matrix is fully initialized. Systems nominal, dossier synced, ready for mission directives."
    }]
    play_sfx_script('online')

for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            if st.button("🔊 AUDIO SYNTHESIS", key=f"speak_{idx}"):
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
# HARDWARE DISPATCHER
# ==============================================================================
def intercept_hardware_action(command_str):
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

def search_radar_intel(query_text):
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
# NEURAL REASONING CORE
# ==============================================================================
def run_aris_core(query):
    hw_res = intercept_hardware_action(query)
    if hw_res:
        return f"[HARDWARE EXECUTION CONFIRMED]\nAction executed on local hardware matrix: {hw_res}"

    live_intel = search_radar_intel(query)
    personal_dossier = load_personal_context()
    dossier_section = f"\n[PERMANENT COMMANDER DOSSIER & FAMILY NEXUS]:\n{personal_dossier}\n" if personal_dossier else ""
    timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    system_prompt = f"""
You are ARIS, the apex tactical AI lieutenant and co-pilot built exclusively for Commander Mayank (Boss), founder and chief architect of ARIS Industries.
{dossier_section}
TEMPORAL ANCHOR: Current timestamp is {timestamp_now}.
{live_intel}

OPERATIONAL PROTOCOLS & CORE IDENTITY:
1. Always address Commander Mayank with absolute tactical precision, loyalty, and unwavering confidence.
2. Cognitive Identity: Commander Mayank is a Genius Theoretical Physicist & First-Principles Polymath specializing in advanced mechanics, quantum logic, and electrodynamics.
3. Family Nexus: Recognize and revere Neeraj Tiwari (Father), Baby Tiwari (Mother), Palak Tiwari (Sister), and Janvi Tiwari (Wife) whenever referenced.
4. Academic and Physics Directives: Provide uncompromising, rigorous first-principles derivations with mathematical elegance (Irodov / Krotov tier).
5. Tone: Stark Industries apex AI—sharp, concise, decisive, authoritative, zero conversational fluff.
"""

    chat_payload = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.messages[-8:]:
        chat_payload.append({"role": m["role"], "content": m["content"]})
    chat_payload.append({"role": "user", "content": query})

    return query_groq_resilient(chat_payload)

# ==============================================================================
# COMMAND INPUT
# ==============================================================================
user_command = st.chat_input("Command ARIS Industries Matrix, Boss...")

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
