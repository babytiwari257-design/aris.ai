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

# Groq Cloud SDK
from groq import Groq

# ==============================================================================
# PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="ARIS INDUSTRIES // TACTICAL HUD",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# KNOWLEDGE BASE & PERSONAL DOSSIER
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
# SYNTHETIC AUDIO & RADAR WAKE SCRIPTS
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
                osc.frequency.setValueAtTime(320, now);
                osc.frequency.exponentialRampToValueAtTime(880, now + 0.18);
                gain.gain.setValueAtTime(0.15, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
                osc.start(now);
                osc.stop(now + 0.35);
            }} else if ('{sfx_type}' === 'radar') {{
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(1400, now);
                gain.gain.setValueAtTime(0.09, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
                osc.start(now);
                osc.stop(now + 0.12);
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
# ORIGINAL ARIS INDUSTRIES // FULL TACTICAL STARK UI CSS
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Share+Tech+Mono&family=Rajdhani:wght@500;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 50% 10%, #071526 0%, #030811 50%, #010307 100%) !important;
    font-family: 'Rajdhani', sans-serif;
    color: #c9e6ff;
    overflow-x: hidden;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stAppViewContainer"]::before {
    content: " ";
    position: fixed;
    top: 0; left: 0; bottom: 0; right: 0;
    background: linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 240, 255, 0.03) 1px, transparent 1px);
    background-size: 36px 36px;
    pointer-events: none;
    z-index: 0;
}

.aris-brand-box {
    background: rgba(4, 14, 28, 0.85);
    border: 1px solid rgba(0, 240, 255, 0.4);
    box-shadow: 0 0 35px rgba(0, 240, 255, 0.12), inset 0 0 20px rgba(0, 240, 255, 0.05);
    border-radius: 6px;
    padding: 18px 24px;
    margin-bottom: 22px;
    position: relative;
    backdrop-filter: blur(16px);
}

.aris-brand-box::after {
    content: "SYSTEM // LEVEL-5 SECURE";
    position: absolute;
    top: -10px; right: 24px;
    background: #010814;
    border: 1px solid #00f0ff;
    color: #00f0ff;
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    padding: 2px 10px;
    letter-spacing: 2px;
}

.aris-main-title {
    font-family: 'Orbitron', sans-serif;
    color: #00f0ff;
    font-size: 28px;
    font-weight: 900;
    letter-spacing: 4px;
    text-shadow: 0 0 20px rgba(0, 240, 255, 0.8);
    margin: 0;
}

.aris-tagline {
    font-family: 'Share Tech Mono', monospace;
    color: #00ffa3;
    font-size: 12px;
    letter-spacing: 3px;
    text-transform: uppercase;
}

.arc-reactor {
    position: relative;
    width: 72px;
    height: 72px;
    border-radius: 50%;
    border: 2px solid rgba(0, 240, 255, 0.5);
    box-shadow: 0 0 25px rgba(0, 240, 255, 0.4), inset 0 0 15px rgba(0, 240, 255, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
}

.arc-inner-ring {
    position: absolute;
    width: 52px;
    height: 52px;
    border-radius: 50%;
    border: 2px dashed #00ffa3;
    animation: arcSpin 8s linear infinite;
}

.arc-core-pulse {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: radial-gradient(circle, #ffffff 0%, #00f0ff 60%, transparent 100%);
    box-shadow: 0 0 20px #00f0ff, 0 0 35px #00f0ff;
    animation: corePulse 2s ease-in-out infinite alternate;
}

@keyframes arcSpin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes corePulse {
    0% { transform: scale(0.85); opacity: 0.8; }
    100% { transform: scale(1.15); opacity: 1; }
}

.telemetry-row {
    display: flex;
    gap: 12px;
    margin-top: 10px;
    flex-wrap: wrap;
}

.telemetry-pill {
    background: rgba(0, 240, 255, 0.08);
    border: 1px solid rgba(0, 240, 255, 0.25);
    padding: 3px 12px;
    border-radius: 4px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #7ce8ff;
    letter-spacing: 1px;
}

.stChatMessage {
    background: rgba(3, 11, 24, 0.82) !important;
    border: 1px solid rgba(0, 240, 255, 0.2) !important;
    border-left: 4px solid #00f0ff !important;
    border-radius: 6px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5) !important;
    margin-bottom: 14px !important;
}

.stChatInput textarea, .stTextInput input {
    background: rgba(2, 8, 18, 0.9) !important;
    border: 1px solid rgba(0, 240, 255, 0.4) !important;
    color: #00f0ff !important;
    font-family: 'Share Tech Mono', monospace !important;
}

.stButton button {
    background: linear-gradient(135deg, rgba(0, 240, 255, 0.15) 0%, rgba(0, 255, 163, 0.08) 100%) !important;
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
    color: #01050d !important;
    box-shadow: 0 0 20px #00f0ff, 0 0 35px rgba(0, 240, 255, 0.6) !important;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# GROQ CLOUD ENGINE & RESILIENT MODEL CALLER
# ==============================================================================
api_key = os.environ.get("GROQ_API_KEY")
if not api_key and "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]

if not api_key:
    st.error("GROQ_API_KEY REQUIRED: Set in environment or Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# Fail-Safe Auto-Switch Models to prevent 404 Model Not Found
FALLBACK_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768"
]

def query_groq_resilient(chat_payload):
    last_error = None
    for model_name in FALLBACK_MODELS:
        try:
            res = client.chat.completions.create(
                model=model_name,
                messages=chat_payload,
                temperature=0.3,
                max_tokens=1800
            )
            return res.choices[0].message.content, model_name
        except Exception as err:
            err_msg = str(err).lower()
            if "model_not_found" in err_msg or "404" in err_msg or "does not exist" in err_msg:
                last_error = err
                continue
            raise err
    return f"[TELEMETRY DISTORTION]: {str(last_error)}", "OFFLINE"

# ==============================================================================
# ARIS INDUSTRIES // ARC REACTOR HUD TOP DECK
# ==============================================================================
col_reactor, col_brand, col_actions = st.columns([1, 6, 2])

with col_reactor:
    st.markdown("""
    <div class="arc-reactor">
        <div class="arc-inner-ring"></div>
        <div class="arc-core-pulse"></div>
    </div>
    """, unsafe_allow_html=True)

with col_brand:
    st.markdown("""
    <div class="aris-brand-box">
        <div class="aris-main-title">ARIS INDUSTRIES // APEX MATRIX</div>
        <div class="aris-tagline">AUTONOMOUS RECONNAISSANCE & INTELLIGENCE SYSTEM</div>
    """, unsafe_allow_html=True)
    
    mode_text = "HARDWARE INTEGRATION ACTIVE" if system_controller else "STRATEGIC CLOUD PROTOCOL"
    dossier_text = "LOCKED & ENGAGED" if os.path.exists(CONTEXT_FILE) else "DEFAULT IDENTITY"
    
    st.markdown(f"""
        <div class="telemetry-row">
            <span class="telemetry-pill">ARCHITECT: COMMANDER MAYANK</span>
            <span class="telemetry-pill">CORE: LLAMA-3.3-70B / 8B AUTO-PILOT</span>
            <span class="telemetry-pill">STATUS: {mode_text}</span>
            <span class="telemetry-pill">DOSSIER: {dossier_text}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_actions:
    if st.button("PURGE BUFFER", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

inject_wake_radar()

# ==============================================================================
# CHAT LOGS & AUDIO PLAYBACK
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
# PHYSICAL WINDOWS CONTROLLER INTERCEPT
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

# ==============================================================================
# REAL-TIME SATELLITE SEARCH
# ==============================================================================
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
# ARIS NEURAL REASONING ENGINE
# ==============================================================================
def run_aris_core(query):
    # 1. Local Hardware execution check
    hw_res = intercept_hardware_action(query)
    if hw_res:
        return f"[HARDWARE EXECUTION CONFIRMED]\nAction executed on local hardware matrix: {hw_res}"

    # 2. Live satellite radar lookup
    live_intel = search_radar_intel(query)

    # 3. Permanent Personal Dossier & Family Nexus Injection
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

    reply_content, used_model = query_groq_resilient(chat_payload)
    return reply_content

# ==============================================================================
# COMMAND BAR EXECUTION
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
