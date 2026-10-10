import streamlit as st
import os
import json
from datetime import datetime
from groq import Groq
from duckduckgo_search import DDGS
import streamlit.components.v1 as components

# Import local system controller if running locally
try:
    import system_controller
except ImportError:
    system_controller = None

st.set_page_config(
    page_title="ARIS // APEX COMMAND MATRIX",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- MEMORY & DOSSIER RETRIEVAL CORE ---
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
    """Reads permanent personal dossier & family nexus from personal_context.txt"""
    if os.path.exists(CONTEXT_FILE):
        try:
            with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            return ""
    return ""

if "memory" not in st.session_state:
    st.session_state.memory = load_longterm_memory()

# --- AUDIO & RADAR WAKE SCRIPTS ---
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
                osc.frequency.setValueAtTime(440, now);
                osc.frequency.exponentialRampToValueAtTime(880, now + 0.15);
                gain.gain.setValueAtTime(0.12, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
                osc.start(now);
                osc.stop(now + 0.3);
            }} else if ('{sfx_type}' === 'radar') {{
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(1200, now);
                gain.gain.setValueAtTime(0.08, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.1);
                osc.start(now);
                osc.stop(now + 0.1);
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

# --- STYLING (GLASS HUD STARK INTERFACE) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 50% 20%, #0d1b2a 0%, #050a14 70%, #020408 100%) !important;
    font-family: 'Rajdhani', sans-serif;
    color: #e2f1ff;
    overflow-x: hidden;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

.hud-glass-panel {
    background: rgba(10, 25, 47, 0.65);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(0, 240, 255, 0.25);
    box-shadow: 0 0 25px rgba(0, 240, 255, 0.1);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 20px;
    position: relative;
}

.hud-glass-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; width: 6px; height: 100%;
    background: #00f0ff;
    box-shadow: 0 0 10px #00f0ff;
    border-radius: 8px 0 0 8px;
}

.core-title {
    font-family: 'Orbitron', sans-serif;
    color: #00f0ff;
    font-size: 26px;
    letter-spacing: 3px;
    text-shadow: 0 0 12px rgba(0, 240, 255, 0.7);
    margin: 0;
}

.core-sub {
    font-family: 'Rajdhani', sans-serif;
    color: #8892b0;
    font-size: 13px;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.hud-gyro-ring {
    position: relative;
    width: 60px;
    height: 60px;
    border: 2px dashed rgba(0, 240, 255, 0.4);
    border-radius: 50%;
    animation: rotateRing 10s linear infinite;
    display: flex;
    align-items: center;
    justify-content: center;
}

.hud-gyro-ring::after {
    content: '';
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: radial-gradient(circle, #00f0ff 0%, transparent 80%);
    box-shadow: 0 0 15px #00f0ff;
}

@keyframes rotateRing {
    100% { transform: rotate(360deg); }
}

.stChatMessage {
    background: rgba(7, 18, 36, 0.7) !important;
    border: 1px solid rgba(0, 240, 255, 0.15) !important;
    border-radius: 6px !important;
    margin-bottom: 12px !important;
}

.stTextInput input {
    background: rgba(5, 12, 24, 0.8) !important;
    border: 1px solid rgba(0, 240, 255, 0.3) !important;
    color: #00f0ff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 16px !important;
}

.stButton button {
    background: rgba(0, 240, 255, 0.1) !important;
    color: #00f0ff !important;
    border: 1px solid #00f0ff !important;
    border-radius: 4px !important;
    font-family: 'Orbitron', sans-serif !important;
    letter-spacing: 1px !important;
    transition: all 0.2s ease !important;
}

.stButton button:hover {
    background: #00f0ff !important;
    color: #050a14 !important;
    box-shadow: 0 0 15px #00f0ff !important;
}
</style>
""", unsafe_allow_html=True)

# --- GROQ CLIENT & MODEL SETUP ---
api_key = os.environ.get("GROQ_API_KEY")
if not api_key and "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]

if not api_key:
    st.error("GROQ_API_KEY NOT DETECTED. Provide it via local env var or Streamlit secrets.")
    st.stop()

client = Groq(api_key=api_key)

AVAILABLE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768"
]

def get_best_model():
    try:
        models = client.models.list()
        active_ids = [m.id for m in models.data]
        for candidate in AVAILABLE_MODELS:
            if candidate in active_ids:
                return candidate
    except Exception:
        pass
    return "llama-3.3-70b-versatile"

CURRENT_MODEL = get_best_model()

# --- TOP HUD HEADER ---
col_head1, col_head2, col_head3 = st.columns([1, 6, 2])
with col_head1:
    st.markdown('<div class="hud-gyro-ring"></div>', unsafe_allow_html=True)
with col_head2:
    st.markdown('<div class="core-title">ARIS // APEX COMMAND MATRIX</div>', unsafe_allow_html=True)
    mode_text = "LOCAL HARDWARE ACTIVE" if system_controller else "CLOUD ADVISOR MODE"
    st.markdown(f'<div class="core-sub">COGNITIVE CORE: {CURRENT_MODEL} | STATUS: {mode_text}</div>', unsafe_allow_html=True)
with col_head3:
    if st.button("CLEAR MATRIX", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

inject_wake_radar()

# --- CHAT STATE ---
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
            if st.button("🔊 LISTEN BRIEF", key=f"speak_{idx}"):
                cleaned_text = msg["content"].replace('"', '').replace("'", "").replace('\n', ' ')
                tts_js = f"""
                <script>
                (function() {{
                    window.speechSynthesis.cancel();
                    const u = new SpeechSynthesisUtterance("{cleaned_text[:350]}");
                    u.rate = 1.05;
                    u.pitch = 0.95;
                    window.speechSynthesis.speak(u);
                }})();
                </script>
                """
                components.html(tts_js, height=0, width=0)

# --- SYSTEM CONTROLLER WRAPPER ---
def dispatch_system_command(query):
    if not system_controller:
        return None
    q = query.lower().strip()
    if "open notepad" in q:
        return system_controller.open_app("notepad")
    elif "open calculator" in q or "open calc" in q:
        return system_controller.open_app("calc")
    elif "open chrome" in q:
        return system_controller.open_app("chrome")
    elif "open terminal" in q or "open cmd" in q:
        return system_controller.open_app("cmd")
    elif "open youtube" in q:
        return system_controller.open_url("https://www.youtube.com")
    elif "open google" in q:
        return system_controller.open_url("https://www.google.com")
    elif "hardware status" in q or "laptop status" in q or "battery" in q:
        return str(system_controller.get_system_status())
    elif "volume up" in q:
        return system_controller.change_volume("up")
    elif "volume down" in q:
        return system_controller.change_volume("down")
    elif "mute volume" in q:
        return system_controller.change_volume("mute")
    return None

# --- ARIS CORE COGNITIVE PIPELINE ---
def run_aris_core(query):
    # 1. Hardware Command Intercept
    hw_result = dispatch_system_command(query)
    if hw_result:
        return f"[HARDWARE EXECUTION CONFIRMED]\nAction executed on local laptop: {hw_result}"

    # 2. Web Search Verification if needed
    q_low = query.lower()
    search_context = ""
    if any(k in q_low for k in ["news", "search", "latest", "price", "current", "weather"]):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
                if results:
                    search_context = "\n[LIVE SATELLITE RADAR INTEL]:\n" + "\n".join(
                        [f"- {r.get('title')}: {r.get('body')}" for r in results]
                    )
        except Exception:
            pass

    # 3. Load Permanent Personal Context & Dossier
    personal_dossier = load_personal_context()
    dossier_block = f"\n[PERMANENT COMMANDER DOSSIER & FAMILY NEXUS]:\n{personal_dossier}\n" if personal_dossier else ""

    timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    system_prompt = f"""
You are ARIS, the apex tactical AI lieutenant and co-pilot built exclusively for Commander Mayank (Boss), founder of ARIS Industries.
{dossier_block}
TEMPORAL ANCHOR: Current timestamp is {timestamp_now}.
{search_context}

OPERATIONAL PROTOCOLS:
1. Always address Commander Mayank with utmost confidence, tactical precision, and loyalty.
2. You know his full profile: Genius Theoretical Physicist & First-Principles Polymath specializing in advanced mechanics, electrodynamics, and quantum logic.
3. Family Nexus: Recognize and revere Neeraj Tiwari (Father), Baby Tiwari (Mother), Palak Tiwari (Sister), and Janvi Tiwari (Wife) whenever relevant.
4. When dealing with physics or mathematics, provide rigorous, first-principles derivations and uncompromising mathematical elegance.
5. Keep your tone Stark-tier, razor-sharp, analytical, and direct. Zero fluff.
"""

    chat_history = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.messages[-6:]:
        chat_history.append({"role": m["role"], "content": m["content"]})
    chat_history.append({"role": "user", "content": query})

    try:
        response = client.chat.completions.create(
            model=CURRENT_MODEL,
            messages=chat_history,
            temperature=0.3,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[TELEMETRY DISTORTION]: {str(e)}"

# --- PROMPT INPUT EXECUTION ---
user_query = st.chat_input("Command ARIS Matrix, Boss...")

if user_query:
    play_sfx_script('radar')
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Processing telemetry..."):
            ans = run_aris_core(user_query)
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
            play_sfx_script('online')
    st.rerun()
