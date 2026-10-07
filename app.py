import streamlit as st
import streamlit.components.v1 as components
import os
import json
from groq import Groq

# --- MATRIX CONFIGURATION ---
st.set_page_config(
    page_title="ARIS // COMMAND MATRIX",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HIGH-CONTRAST READABLE COMBAT HUD STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800;900&family=Inter:wght@400;500;600;700&display=swap');

    /* Global Background: Deep Carbon Black for maximum readability */
    .stApp {
        background-color: #05080f !important;
        background-image: radial-gradient(circle at 50% 0%, #0d1b2a 0%, #05080f 80%) !important;
        color: #f1f5f9 !important;
        font-family: 'Inter', sans-serif !important;
    }
    header, footer { visibility: hidden !important; }

    /* Header Bar */
    .hud-title-box {
        background: #09131f;
        border: 1px solid #00e5ff;
        border-radius: 12px;
        padding: 16px 24px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 229, 255, 0.15);
        margin-bottom: 12px;
    }
    .hud-title {
        font-family: 'Orbitron', sans-serif;
        color: #00e5ff;
        font-size: 26px;
        font-weight: 900;
        letter-spacing: 3px;
        margin: 0;
    }
    .hud-subtitle {
        color: #94a3b8;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 2px;
        margin-top: 6px;
        text-transform: uppercase;
    }

    /* Telemetry Cards */
    .telemetry-card {
        background: #0d1829;
        border: 1px solid #1e3a5f;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        font-size: 11px;
        color: #38bdf8;
    }
    .telemetry-val {
        color: #ffffff;
        font-size: 14px;
        font-weight: 700;
        margin-top: 2px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    /* Chat Messages: Pure contrast for effortless reading */
    [data-testid="stChatMessage"] {
        padding: 14px 18px !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
        line-height: 1.6 !important;
        font-size: 15px !important;
    }
    /* ARIS Message Bubble */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #0b1a2e !important;
        border: 1px solid #0284c7 !important;
        color: #f8fafc !important;
    }
    /* User Message Bubble */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #081320 !important;
        border: 1px solid #1e293b !important;
        color: #e2e8f0 !important;
    }

    /* Message inner markdown text force-bright */
    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] li, 
    [data-testid="stChatMessage"] span {
        color: #f8fafc !important;
        font-weight: 400 !important;
    }
    [data-testid="stChatMessage"] strong {
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }

    /* Code Blocks within chat */
    pre, code {
        background-color: #030712 !important;
        color: #38bdf8 !important;
        border: 1px solid #1f2937 !important;
        border-radius: 6px !important;
    }

    /* Chat Input Area */
    .stTextInput input, .stChatInput textarea {
        background-color: #0b1320 !important;
        border: 1px solid #0284c7 !important;
        color: #ffffff !important;
        font-size: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- LONG TERM MEMORY VAULT ---
MEMORY_FILE = "aris_longterm_vault.json"

def load_longterm_memory():
    defaults = [
        "Supreme Commander: Mayank (Boss).",
        "Identity Protocol: ARIS, tactical AI partner."
    ]
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return defaults
    return defaults

def save_longterm_memory(memories):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memories, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# --- SESSION INITIALIZATIONS ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "memory_vault" not in st.session_state:
    st.session_state.memory_vault = load_longterm_memory()

# --- GROQ CLIENT RETRIEVER ---
def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key.strip())

# --- DYNAMIC ACTIVE TEXT MODEL DISCOVERY ---
@st.cache_data(ttl=900)
def discover_usable_models():
    client = get_groq_client()
    priority_order = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.8-27b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]
    if not client:
        return priority_order

    try:
        live_catalog = client.models.list()
        all_ids = [m.id for m in live_catalog.data if getattr(m, 'active', True)]

        clean_models = [
            m_id for m_id in all_ids
            if not any(blocked in m_id.lower() for blocked in [
                "whisper", "guard", "orpheus", "prompt-guard", "safeguard", "compound"
            ])
        ]

        sorted_models = []
        for pref in priority_order:
            if pref in clean_models:
                sorted_models.append(pref)
        for m_id in clean_models:
            if m_id not in sorted_models:
                sorted_models.append(m_id)

        return sorted_models if sorted_models else priority_order
    except Exception:
        return priority_order

active_models_list = discover_usable_models()
primary_model_name = active_models_list[0] if active_models_list else "openai/gpt-oss-120b"

# --- 3D INTERACTIVE HOLO-REACTOR & AUDIO ENGINE ---
holo_reactor_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; overflow: hidden; background: transparent; }
  #canvas-container { width: 100%; height: 210px; position: relative; }
  #voice-btn {
    position: absolute;
    bottom: 6px;
    left: 50%;
    transform: translateX(-50%);
    background: #0b1a2e;
    border: 1px solid #00e5ff;
    color: #00e5ff;
    font-family: 'Orbitron', monospace;
    font-size: 11px;
    font-weight: bold;
    padding: 7px 18px;
    border-radius: 20px;
    cursor: pointer;
    box-shadow: 0 0 15px rgba(0, 229, 255, 0.3);
    transition: all 0.25s;
    letter-spacing: 1.5px;
  }
  #voice-btn:hover {
    background: #00e5ff;
    color: #05080f;
    box-shadow: 0 0 25px #00e5ff;
  }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
<div id="canvas-container">
  <button id="voice-btn" onclick="toggleVoiceTransmission()">🎙️ TRANSMIT AUDIO [HOLD TO TALK]</button>
</div>

<script>
  const container = document.getElementById('canvas-container');
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
  const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);

  const group = new THREE.Group();
  scene.add(group);

  const ring1 = new THREE.Mesh(
    new THREE.TorusGeometry(2.3, 0.03, 16, 90),
    new THREE.MeshBasicMaterial({ color: 0x00e5ff, wireframe: true })
  );
  group.add(ring1);

  const ring2 = new THREE.Mesh(
    new THREE.TorusGeometry(1.7, 0.04, 16, 75),
    new THREE.MeshBasicMaterial({ color: 0x0284c7, wireframe: true })
  );
  group.add(ring2);

  const core = new THREE.Mesh(
    new THREE.IcosahedronGeometry(0.85, 2),
    new THREE.MeshBasicMaterial({ color: 0x38bdf8, wireframe: true })
  );
  group.add(core);

  camera.position.z = 5.8;

  let mouseX = 0, mouseY = 0;
  window.addEventListener('mousemove', (e) => {
    const rect = container.getBoundingClientRect();
    mouseX = ((e.clientX - rect.left) / container.clientWidth) * 2 - 1;
    mouseY = -(((e.clientY - rect.top) / container.clientHeight) * 2 - 1);
  });

  function animate() {
    requestAnimationFrame(animate);
    ring1.rotation.z += 0.01;
    ring2.rotation.x -= 0.012;
    core.rotation.y += 0.016;

    group.rotation.y += (mouseX * 0.7 - group.rotation.y) * 0.06;
    group.rotation.x += (-mouseY * 0.7 - group.rotation.x) * 0.06;

    renderer.render(scene, camera);
  }
  animate();

  let recognition;
  function toggleVoiceTransmission() {
    const btn = document.getElementById('voice-btn');
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert("Browser speech recognition not supported.");
      return;
    }
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRec();
    recognition.lang = 'en-IN';
    recognition.start();

    btn.innerText = "🔴 LISTENING TO BOSS...";
    btn.style.borderColor = "#ff0055";
    btn.style.color = "#ff0055";

    recognition.onresult = function(e) {
      const transcript = e.results[0][0].transcript;
      btn.innerText = "⚡ TRANSMITTING...";
      const input = window.parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
      if (input) {
        input.value = transcript;
        input.dispatchEvent(new Event('input', { bubbles: true }));
        const submitBtn = window.parent.document.querySelector('button[data-testid="stChatInputSubmitButton"]');
        if (submitBtn) submitBtn.click();
      }
    };
    recognition.onend = function() {
      btn.innerText = "🎙️ TRANSMIT AUDIO [HOLD TO TALK]";
      btn.style.borderColor = "#00e5ff";
      btn.style.color = "#00e5ff";
    };
  }
</script>
</body>
</html>
"""

# --- NATURAL HUMAN TTS VOICE PICKER ---
def aris_speak(text):
    clean = str(text).replace('*', '').replace('#', '').replace('`', '').replace('"', '').replace("'", "")
    clean = clean.replace('\n', ' ')[:220]
    js = f"""
    <script>
      function speakVoice() {{
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel();
        var utter = new SpeechSynthesisUtterance('{clean}');
        var voices = window.speechSynthesis.getVoices();
        
        var selected = voices.find(v => 
          (v.name.includes("Natural") && (v.lang.includes("IN") || v.lang.includes("hi"))) ||
          v.name.includes("Neerja") ||
          v.name.includes("Prabhat") ||
          v.name.includes("Google हिन्दी") ||
          v.lang === "en-IN"
        );
        if (!selected) {{
          selected = voices.find(v => v.lang === "en-US" || v.name.includes("Natural"));
