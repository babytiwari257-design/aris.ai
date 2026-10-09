import streamlit as st
import streamlit.components.v1 as components
import os
import json
import base64
import re
from datetime import datetime
from groq import Groq

# --- SYSTEM CONTROLLER HARDWARE LINK (SAFE FALLBACK) ---
try:
    from system_controller import execute_os_action, get_live_telemetry
    HARDWARE_ONLINE = True
except Exception:
    HARDWARE_ONLINE = False
    def execute_os_action(action_tag, target=""):
        return "Hardware link standby (system_controller module missing)."
    def get_live_telemetry():
        return "Telemetry Standby"

# --- MATRIX CONFIGURATION ---
st.set_page_config(
    page_title="ARIS // APEX COMMAND MATRIX",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HIGH-TECH VECTOR SVG AVATARS (BASE64) ---
USER_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <polygon points="50,6 90,26 90,74 50,94 10,74 10,26" fill="#08182b" stroke="#38bdf8" stroke-width="5"/>
  <circle cx="50" cy="50" r="15" fill="#38bdf8"/>
  <line x1="50" y1="18" x2="50" y2="32" stroke="#00e5ff" stroke-width="4"/>
  <line x1="50" y1="68" x2="50" y2="82" stroke="#00e5ff" stroke-width="4"/>
  <line x1="18" y1="50" x2="32" y2="50" stroke="#00e5ff" stroke-width="4"/>
  <line x1="68" y1="50" x2="82" y2="50" stroke="#00e5ff" stroke-width="4"/>
</svg>"""

ARIS_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="44" fill="#040e1c" stroke="#00e5ff" stroke-width="5"/>
  <circle cx="50" cy="28" fill="none" stroke="#38bdf8" stroke-width="3.5" stroke-dasharray="10,5"/>
  <polygon points="50,28 68,64 32,64" fill="#00e5ff"/>
  <circle cx="50" cy="6" r="3" fill="#ffffff"/>
  <circle cx="50" cy="50" r="6" fill="#ffffff"/>
</svg>"""

user_avatar = f"data:image/svg+xml;base64,{base64.b64encode(USER_SVG.encode()).decode()}"
aris_avatar = f"data:image/svg+xml;base64,{base64.b64encode(ARIS_SVG.encode()).decode()}"

# --- HUD STYLING & GLASS CONTRAST ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;700;800;900&family=Rajdhani:wght@500;600;700&display=swap');

    .stApp {
        background: 
            radial-gradient(circle at 50% 0%, rgba(0, 229, 255, 0.09) 0%, transparent 60%),
            radial-gradient(circle at 10% 80%, rgba(2, 132, 199, 0.05) 0%, transparent 40%),
            linear-gradient(rgba(0, 229, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 229, 255, 0.03) 1px, transparent 1px),
            #030712 !important;
        background-size: 100% 100%, 100% 100%, 35px 35px, 35px 35px, 100% 100% !important;
        color: #f8fafc !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    header, footer { visibility: hidden !important; }

    .hud-title-box {
        background: rgba(9, 20, 36, 0.88);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(0, 229, 255, 0.55);
        border-radius: 14px;
        padding: 16px 28px;
        text-align: center;
        box-shadow: 0 0 25px rgba(0, 229, 255, 0.18), inset 0 0 15px rgba(0, 229, 255, 0.06);
        margin-bottom: 12px;
    }
    .hud-title {
        font-family: 'Orbitron', sans-serif;
        color: #00e5ff;
        font-size: 27px;
        font-weight: 900;
        letter-spacing: 4px;
        text-shadow: 0 0 16px rgba(0, 229, 255, 0.6);
        margin: 0;
    }
    .hud-subtitle {
        color: #38bdf8;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 3px;
        margin-top: 6px;
        text-transform: uppercase;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
    }

    .telemetry-card {
        background: rgba(8, 22, 40, 0.75);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(2, 132, 199, 0.4);
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        font-size: 11px;
        color: #38bdf8;
        box-shadow: inset 0 0 12px rgba(0, 229, 255, 0.05);
        transition: all 0.3s ease;
    }
    .telemetry-val {
        color: #ffffff;
        font-size: 13px;
        font-weight: 700;
        margin-top: 3px;
        text-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    [data-testid="stChatMessage"] {
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        padding: 16px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 8px !important;
        line-height: 1.65 !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }
    [data-testid="stChatMessage"]:nth-child(even) {
        background: rgba(8, 26, 48, 0.9) !important;
        border: 1px solid rgba(0, 229, 255, 0.55) !important;
        box-shadow: 0 4px 20px rgba(0, 229, 255, 0.12), inset 0 0 10px rgba(0, 229, 255, 0.04) !important;
    }
    [data-testid="stChatMessage"]:nth-child(odd) {
        background: rgba(14, 30, 52, 0.8) !important;
        border: 1px solid rgba(56, 189, 248, 0.35) !important;
    }

    [data-testid="stChatMessageAvatar"] {
        background: transparent !important;
        border-radius: 50% !important;
        box-shadow: 0 0 12px rgba(0, 229, 255, 0.5) !important;
    }

    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] li, 
    [data-testid="stChatMessage"] span {
        color: #f8fafc !important;
    }
    [data-testid="stChatMessage"] strong {
        color: #00e5ff !important;
        text-shadow: 0 0 8px rgba(0, 229, 255, 0.4) !important;
    }

    .stButton>button {
        background: rgba(8, 26, 48, 0.9) !important;
        border: 1px solid #00e5ff !important;
        color: #00e5ff !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        border-radius: 20px !important;
        padding: 4px 14px !important;
        transition: all 0.25s ease !important;
        margin-bottom: 12px !important;
    }
    .stButton>button:hover {
        background: #00e5ff !important;
        color: #030712 !important;
        box-shadow: 0 0 15px #00e5ff !important;
    }

    .stTextInput input, .stChatInput textarea {
        background: rgba(6, 18, 32, 0.9) !important;
        border: 1px solid rgba(0, 229, 255, 0.6) !important;
        color: #ffffff !important;
        font-size: 16px !important;
        border-radius: 10px !important;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.15) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- LONG TERM MEMORY VAULT ---
MEMORY_FILE = "aris_longterm_vault.json"

def load_longterm_memory():
    defaults = [
        "Creator & Founder of ARIS Industries: Commander Mayank (Boss).",
        "Identity Protocol: ARIS, high-level tactical AI matrix."
    ]
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return defaults
    return defaults

# --- SESSION STATES ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "memory_vault" not in st.session_state:
    st.session_state.memory_vault = load_longterm_memory()
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
            if any(blocked in m_id for blocked in ["whisper", "guard", "orpheus", "prompt-guard", "safeguard", "compound"]):
                continue
            usable.append(m.id)
        
        priority_keywords = ["120b", "70b", "27b", "20b", "8b"]
        sorted_models = []
        for kw in priority_keywords:
            for u in usable:
                if kw in u.lower() and u not in sorted_models:
                    sorted_models.append(u)
        for u in usable:
            if u not in sorted_models:
                sorted_models.append(u)
        return sorted_models if sorted_models else ["llama-3.1-8b-instant"]
    except Exception:
        return ["llama-3.1-8b-instant"]

live_active_models = get_live_groq_models()

# --- HOLOGRAPHIC CORE & RADAR WITH SFX ---
aris_legendary_reactor_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; overflow: hidden; background: transparent; display: flex; justify-content: center; align-items: center; }
  #hologram-stage {
    position: relative;
    width: 100%;
    height: 280px;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .energy-ring-outer {
    position: absolute;
    width: 250px;
    height: 250px;
    border-radius: 50%;
    border: 1px dashed rgba(0, 229, 255, 0.35);
    box-shadow: 0 0 30px rgba(0, 229, 255, 0.15);
    animation: spinClockwise 22s linear infinite;
  }
  .energy-ring-inner {
    position: absolute;
    width: 215px;
    height: 215px;
    border-radius: 50%;
    border-top: 3px solid #00e5ff;
    border-bottom: 3px solid #0284c7;
    border-left: 1px solid transparent;
    border-right: 1px solid transparent;
    box-shadow: 0 0 25px rgba(0, 229, 255, 0.5);
    animation: spinCounter 12s linear infinite;
  }
  .logo-core {
    position: relative;
    width: 175px;
    height: 175px;
    border-radius: 50%;
    background: radial-gradient(circle, #071526 30%, #030a14 80%, #010408 100%);
    box-shadow: 0 0 40px rgba(0, 229, 255, 0.6), inset 0 0 25px rgba(0, 229, 255, 0.4);
    border: 2px solid rgba(0, 229, 255, 0.7);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    animation: reactorPulse 3.5s ease-in-out infinite;
    transform-style: preserve-3d;
    transition: transform 0.1s ease-out;
  }
  .insignia-svg {
    width: 110px;
    height: 110px;
    filter: drop-shadow(0 0 10px rgba(0, 229, 255, 0.8));
    animation: circuitPulse 2.5s ease-in-out infinite;
  }
  .brand-text {
    font-family: 'Orbitron', sans-serif;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 3px;
    color: #e2e8f0;
    margin-top: 4px;
    text-shadow: 0 0 8px rgba(0, 229, 255, 0.8);
  }
  @keyframes spinClockwise { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
  @keyframes spinCounter { from { transform: rotate(0deg); } to { transform: rotate(-360deg); } }
  @keyframes reactorPulse {
    0%, 100% { transform: scale(1); box-shadow: 0 0 35px rgba(0, 229, 255, 0.5), inset 0 0 18px rgba(0, 229, 255, 0.35); }
    50% { transform: scale(1.03); box-shadow: 0 0 55px rgba(0, 229, 255, 0.85), inset 0 0 28px rgba(0, 229, 255, 0.6); }
  }
  @keyframes circuitPulse {
    0%, 100% { opacity: 0.9; }
    50% { opacity: 1; filter: drop-shadow(0 0 16px rgba(0, 229, 255, 1)); }
  }
  .control-hud {
    position: absolute;
    bottom: 2px;
    display: flex;
    gap: 12px;
  }
  .hud-btn {
    background: rgba(9, 24, 44, 0.85);
    border: 1px solid #00e5ff;
    color: #00e5ff;
    font-family: 'Orbitron', sans-serif;
    font-size: 10px;
    font-weight: 700;
    padding: 6px 18px;
    border-radius: 20px;
    cursor: pointer;
    box-shadow: 0 0 15px rgba(0, 229, 255, 0.35);
    transition: all 0.25s ease;
    letter-spacing: 1.5px;
  }
  .hud-btn:hover { background: #00e5ff; color: #030712; box-shadow: 0 0 25px #00e5ff; }
</style>
</head>
<body>
<div id="hologram-stage">
  <div class="energy-ring-outer"></div>
  <div class="energy-ring-inner"></div>
  <div class="logo-core" id="logoBox">
    <svg class="insignia-svg" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="metallicChrome" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#94a3b8" />
          <stop offset="35%" stop-color="#f8fafc" />
          <stop offset="60%" stop-color="#475569" />
          <stop offset="100%" stop-color="#cbd5e1" />
        </linearGradient>
        <linearGradient id="cyanCircuit" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#00e5ff" />
          <stop offset="100%" stop-color="#0284c7" />
        </linearGradient>
      </defs>
      <polygon points="100,22 175,65 175,135 100,178 25,135 25,65" stroke="#00e5ff" stroke-width="2.5" fill="none" opacity="0.4" />
      <path d="M 100,32 L 152,142 L 126,142 L 114,116 L 86,116 L 74,142 L 48,142 Z" fill="url(#metallicChrome)" stroke="#00e5ff" stroke-width="2" />
      <polygon points="100,68 111,94 89,94" fill="#030a14" stroke="#00e5ff" stroke-width="1.5" />
      <path d="M 66,118 L 84,74" stroke="url(#cyanCircuit)" stroke-width="2.5" stroke-linecap="round" />
      <circle cx="66" cy="118" r="3" fill="#00e5ff" />
      <path d="M 134,118 L 116,74" stroke="url(#cyanCircuit)" stroke-width="2.5" stroke-linecap="round" />
      <circle cx="134" cy="118" r="3" fill="#00e5ff" />
      <circle cx="100" cy="50" r="3.5" fill="#00e5ff" />
    </svg>
    <div class="brand-text">ARIS INDUSTRIES</div>
  </div>
  <div class="control-hud">
    <button class="hud-btn" id="voice-btn" onclick="toggleVoiceTransmission()">🎙️ TRANSMIT AUDIO</button>
    <button class="hud-btn" id="radar-btn" onclick="togglePassiveRadar()">📡 RADAR WAKE: OFF</button>
  </div>
</div>
<script>
  const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  function playArcSfx(type) {
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    if (type === 'chirp') {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(800, audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(1600, audioCtx.currentTime + 0.12);
      gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.12);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.12);
    } else if (type === 'powerup') {
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(110, audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(440, audioCtx.currentTime + 0.35);
      gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.35);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.35);
    }
  }

  const stage = document.getElementById('hologram-stage');
  const logo = document.getElementById('logoBox');
  stage.addEventListener('mousemove', (e) => {
    const rect = stage.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    logo.style.transform = `perspective(600px) rotateY(${x * 0.12}deg) rotateX(${-y * 0.12}deg)`;
  });
  stage.addEventListener('mouseleave', () => {
    logo.style.transform = 'perspective(600px) rotateY(0deg) rotateX(0deg)';
  });

  let recognition;
  function toggleVoiceTransmission() {
    playArcSfx('chirp');
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) return;
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRec();
    recognition.lang = 'en-IN';
    recognition.start();

    const btn = document.getElementById('voice-btn');
    btn.innerText = "🔴 LISTENING...";
    btn.style.borderColor = "#ff0055";
    btn.style.color = "#ff0055";

    recognition.onresult = function(e) {
      const transcript = e.results[0][0].transcript;
      btn.innerText = "⚡ TRANSMITTING...";
      playArcSfx('powerup');
      const input = window.parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
      if (input) {
        input.value = transcript;
        input.dispatchEvent(new Event('input', { bubbles: true }));
        const submitBtn = window.parent.document.querySelector('button[data-testid="stChatInputSubmitButton"]');
        if (submitBtn) submitBtn.click();
      }
    };
    recognition.onend = function() {
      btn.innerText = "🎙️ TRANSMIT AUDIO";
      btn.style.borderColor = "#00e5ff";
      btn.style.color = "#00e5ff";
    };
  }

  let passiveRadarActive = false;
  let radarRec;
  function togglePassiveRadar() {
    playArcSfx('chirp');
    const rBtn = document.getElementById('radar-btn');
    if (!passiveRadarActive) {
      if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) return;
      const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
      radarRec = new SpeechRec();
      radarRec.continuous = true;
      radarRec.interimResults = false;
      radarRec.lang = 'en-IN';

      radarRec.onresult = function(e) {
        const last = e.results.length - 1;
        const heard = e.results[last][0].transcript.toLowerCase();
        if (heard.includes('aris') || heard.includes('hey aris') || heard.includes('boss')) {
          playArcSfx('powerup');
          toggleVoiceTransmission();
        }
      };

      radarRec.onend = function() {
        if (passiveRadarActive) radarRec.start();
      };

      radarRec.start();
      passiveRadarActive = true;
      rBtn.innerText = "📡 RADAR: LISTENING";
      rBtn.style.borderColor = "#38bdf8";
      rBtn.style.color = "#38bdf8";
    } else {
      passiveRadarActive = false;
      if (radarRec) radarRec.stop();
      rBtn.innerText = "📡 RADAR WAKE: OFF";
      rBtn.style.borderColor = "#00e5ff";
      rBtn.style.color = "#00e5ff";
    }
  }
</script>
</body>
</html>
"""

# --- ON-DEMAND GEMINI AUDIO BRIEF ENGINE ---
def trigger_audio_brief(text):
    clean = str(text).replace('*', '').replace('#', '').replace('`', '').replace('"', '').replace("'", "")
    clean = clean.replace('\n', ' ')[:220]
    
    js = f"""
    <script>
      function speakVoice() {{
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel();
        var utter = new SpeechSynthesisUtterance('{clean}');
        var voices = window.speechSynthesis.getVoices();
        var selected = voices.find(function(v) {{
          return (v.name.includes("Natural") && (v.lang.includes("IN") || v.lang.includes("hi"))) ||
                 v.name.includes("Neerja") ||
                 v.name.includes("Prabhat") ||
                 v.name.includes("Google हिन्दी") ||
                 v.lang === "hi-IN";
        }});
        if (!selected) {{
          selected = voices.find(function(v) {{
            return v.lang === "en-IN" || v.lang === "en-US" || v.name.includes("Natural");
          }});
        }}
        if (selected) utter.voice = selected;
        utter.pitch = 1.0;
        utter.rate = 1.05;
        window.speechSynthesis.speak(utter);
      }}
      if (window.speechSynthesis.getVoices().length === 0) {{
        window.speechSynthesis.onvoiceschanged = speakVoice;
      }} else {{
        speakVoice();
      }}
    </script>
    """
    components.html(js, height=0, width=0)

# --- HEADER INTERFACE ---
status_subtitle = "ARIS IS MY CO-PILOT // HARDWARE BRIDGE ARMED // MAYANK"

st.markdown(
    '<div class="hud-title-box">'
    '<h1 class="hud-title">ARIS // APEX COMMAND MATRIX</h1>'
    f'<div class="hud-subtitle">{status_subtitle}</div>'
    '</div>',
    unsafe_allow_html=True
)

components.html(aris_legendary_reactor_html, height=285)

# STARK-TIER TELEMETRY HUD
active_display_core = "ONLINE"
if live_active_models:
    raw_name = str(live_active_models[0])
    parts = raw_name.split("/")
    active_display_core = parts[-1].upper()

c1, c2, c3, c4 = st.columns(4)
with c1:
    stat_val = "COMMANDER ACTIVE" if st.session_state.is_boss_authenticated else "GUEST RESTRICTED"
    st.markdown(f'<div class="telemetry-card">SYNAPSE MATRIX<div class="telemetry-val">{stat_val}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="telemetry-card">LOGIC NEURAL CORE<div class="telemetry-val">{active_display_core}</div></div>', unsafe_allow_html=True)
with c3:
    hw_status = "ONLINE & LINKED" if HARDWARE_ONLINE else "STANDBY"
    st.markdown(f'<div class="telemetry-card">OS HARDWARE BRIDGE<div class="telemetry-val">{hw_status}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="telemetry-card">ENGRAM ARCHIVE<div class="telemetry-val">{len(st.session_state.memory_vault)} SECURE NODES</div></div>', unsafe_allow_html=True)

st.write("")

# --- INFERENCE ENGINE WITH HARDWARE ACTION TAGGING ---
def run_aris_core(query):
    client = get_groq_client()
    if not client:
        yield "API key not configured in environment."
        return

    memories = "\n".join([f"- {m}" for m in st.session_state.memory_vault])
    timestamp_now = datetime.now().strftime("%A, %d %B %Y, %I:%M %p")

    system_prompt = f"""
You are ARIS, the apex tactical AI lieutenant and co-pilot built exclusively for Commander Mayank (Boss), founder of ARIS Industries.
TEMPORAL ANCHOR: Current timestamp is {timestamp_now}.

COGNITIVE DIRECTIVES:
1. Mayank is your Commander, Boss, Creator, and the Founder of ARIS Industries. Greet him with genuine tactical confidence and respect.
2. For academic, physics, math (Irodov, Krotov, etc.) or technical questions: Use First-Principles thinking. Provide precise step-by-step derivations and formulas.
3. HARDWARE & OPERATING SYSTEM EXECUTION PROTOCOLS:
   - You are directly connected to Commander Mayank's laptop hardware via `system_controller`.
   - If Boss asks you to perform an action on the PC, ALWAYS include an exact action tag in your response:
     * Open applications: `[ACTION: OPEN_APP, target: chrome]` (or target: code, notepad, calc, cmd, etc.)
     * Adjust audio: `[ACTION: VOLUME, target: up]`, `[ACTION: VOLUME, target: down]`, `[ACTION: VOLUME, target: mute]`
     * Capture screen: `[ACTION: SCREENSHOT]`
     * Lock PC: `[ACTION: LOCK]`
     * Read battery/CPU metrics: `[ACTION: TELEMETRY]`
   - Acknowledge the hardware command cleanly with tactical confidence.

DUAL-STREAM PROTOCOL:
At the very end of your response, provide a 1-sentence vocal brief enclosed in [VOICE: <brief>].
[ARCHIVED DIRECTIVES]:
{memories}
"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.chat_history[-4:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": query})

    stream_success = False
    last_err = ""

    for candidate_model in live_active_models:
        try:
            completion = client.chat.completions.create(
                model=candidate_model,
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
        yield f"Neural link failed across all live cores: {last_err}"

# --- TIMELINE RENDER (WITH GEMINI-STYLE VOICE BUTTON) ---
for idx, msg in enumerate(st.session_state.chat_history):
    curr_avatar = aris_avatar if msg["role"] == "assistant" else user_avatar
    with st.chat_message(msg["role"], avatar=curr_avatar):
        clean_display = re.sub(r'\[VOICE:\s*(.*?)\]', '', msg["content"])
        clean_display = re.sub(r'\[ACTION:\s*[^\]]+\]', '', clean_display).strip()
        st.markdown(clean_display)
        
        if msg["role"] == "assistant":
            voice_match = re.search(r'\[VOICE:\s*(.*?)\]', msg["content"])
            vocal_summary = voice_match.group(1) if voice_match else clean_display[:180]
            if st.button("🔊 LISTEN BRIEF", key=f"voice_btn_{idx}"):
                trigger_audio_brief(vocal_summary)

# --- USER COMMAND DISPATCH ---
user_input = st.chat_input("Command ARIS Matrix, Boss...")

if user_input:
    q_norm = user_input.lower().strip()
    
    boss_patterns = [
        r"\b(main|me)\s*(hu|hoo)\s*mayank\b",
        r"\bmayank\s*(hu|hoo|here)\b",
        r"\bboss\s*(here|hu|hoo|agya|aagaya|is\s*here)\b",
        r"\bcommander\s*mayank\b",
        r"\bi\s*am\s*mayank\b"
    ]
    
    just_authenticated = False
    if not st.session_state.is_boss_authenticated:
        if any(re.search(pat, q_norm) for pat in boss_patterns):
            st.session_state.is_boss_authenticated = True
            just_authenticated = True

    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar=user_avatar):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar=aris_avatar):
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

        # --- PARSE & EXECUTE HARDWARE OS ACTIONS ---
        action_match = re.search(r'\[ACTION:\s*(\w+)(?:,\s*target:\s*([^\]]+))?\]', full_resp)
        if action_match:
            act_type = action_match.group(1)
            act_target = action_match.group(2) or ""
            execution_report = execute_os_action(act_type, act_target)
            st.toast(f"💠 {execution_report}")

    if just_authenticated:
        st.rerun()
