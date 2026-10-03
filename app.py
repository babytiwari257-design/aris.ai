import streamlit as st
import streamlit.components.v1 as components
import os
import time
from groq import Groq

# --- MATRIX CONFIGURATION ---
st.set_page_config(
    page_title="ARIS // COMMAND MATRIX",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CYBERPUNK HUD WAR-ROOM STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap');

    .stApp {
        background: radial-gradient(circle at 50% 15%, #051622 0%, #01060a 100%);
        color: #d1ecf1;
        font-family: 'Rajdhani', sans-serif;
    }
    header, footer { visibility: hidden !important; }

    .hud-title-box {
        background: linear-gradient(135deg, rgba(2, 28, 48, 0.95) 0%, rgba(1, 10, 20, 0.98) 100%);
        border: 1px solid #00f3ff;
        border-radius: 12px;
        padding: 16px 24px;
        text-align: center;
        box-shadow: 0 0 35px rgba(0, 243, 255, 0.35), inset 0 0 15px rgba(0, 243, 255, 0.15);
        margin-bottom: 8px;
    }
    .hud-title {
        font-family: 'Orbitron', sans-serif;
        color: #00f3ff;
        font-size: 26px;
        font-weight: 900;
        letter-spacing: 4px;
        text-shadow: 0 0 15px rgba(0, 243, 255, 0.8);
        margin: 0;
    }
    .hud-subtitle {
        color: #38bdf8;
        font-size: 11px;
        letter-spacing: 3px;
        margin-top: 4px;
        text-transform: uppercase;
    }

    .telemetry-card {
        background: rgba(4, 18, 30, 0.85);
        border: 1px solid rgba(0, 243, 255, 0.3);
        border-radius: 8px;
        padding: 8px;
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        font-size: 11px;
        color: #38bdf8;
        box-shadow: inset 0 0 10px rgba(0, 243, 255, 0.15);
    }
    .telemetry-val {
        color: #ffffff;
        font-size: 14px;
        font-weight: bold;
        text-shadow: 0 0 8px rgba(0, 243, 255, 0.8);
    }

    [data-testid="stChatMessage"]:nth-child(even) {
        background: rgba(3, 25, 40, 0.85) !important;
        border: 1px solid #00f3ff !important;
        border-radius: 10px;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.15);
    }
    [data-testid="stChatMessage"]:nth-child(odd) {
        background: rgba(8, 32, 54, 0.75) !important;
        border: 1px solid #0284c7 !important;
        border-radius: 10px;
    }
    .stTextInput input, .stChatInput textarea {
        background-color: #030d17 !important;
        border: 1px solid #00f3ff !important;
        color: #00f3ff !important;
    }
</style>
""", unsafe_allow_html=True)

# --- CLIENT INITIALIZATION ---
def get_groq_client():
    api_key = (
        st.session_state.get("manual_key", "")
        or st.secrets.get("GROQ_API_KEY")
        or os.environ.get("GROQ_API_KEY")
    )
    if not api_key:
        return None
    return Groq(api_key=api_key.strip())

# --- DYNAMIC ACTIVE MODEL SELECTOR ---
@st.cache_data(ttl=1800)
def resolve_active_groq_model():
    client = get_groq_client()
    if not client:
        return "llama-3.3-70b-versatile"
    preferred = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    try:
        models = client.models.list()
        active = [m.id for m in models.data if getattr(m, 'active', True)]
        for p in preferred:
            if p in active:
                return p
        for m in active:
            if "whisper" not in m.lower() and "guard" not in m.lower():
                return m
    except Exception:
        pass
    return "llama-3.3-70b-versatile"

# --- SESSION STATES ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "memory_vault" not in st.session_state:
    st.session_state.memory_vault = [
        "Supreme Commander: Boss.",
        "Primary Directive: 100% Loyal, Sharp Hinglish Execution."
    ]
if "manual_key" not in st.session_state:
    st.session_state.manual_key = ""

# --- WEB AUDIO SYNTHESIZER (HUD BEEP) ---
def trigger_tactical_sfx():
    sfx_js = """
    <script>
      (function() {
        try {
          const AudioContext = window.AudioContext || window.webkitAudioContext;
          if (!AudioContext) return;
          const ctx = new AudioContext();
          const now = ctx.currentTime;
          
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();

          osc.type = 'sine';
          osc.frequency.setValueAtTime(800, now);
          osc.frequency.exponentialRampToValueAtTime(1600, now + 0.08);

          gain.gain.setValueAtTime(0.06, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.1);

          osc.connect(gain);
          gain.connect(ctx.destination);

          osc.start(now);
          osc.stop(now + 0.1);
        } catch(e) {}
      })();
    </script>
    """
    components.html(sfx_js, height=0, width=0)

# --- 3D INTERACTIVE HOLO-REACTOR & AUDIO ENGINE ---
holo_reactor_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; overflow: hidden; background: transparent; }
  #canvas-container { width: 100%; height: 250px; position: relative; }
  #voice-btn {
    position: absolute;
    bottom: 10px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0, 243, 255, 0.15);
    border: 1px solid #00f3ff;
    color: #00f3ff;
    font-family: 'Orbitron', monospace;
    font-size: 11px;
    padding: 6px 16px;
    border-radius: 20px;
    cursor: pointer;
    box-shadow: 0 0 15px rgba(0, 243, 255, 0.4);
    transition: all 0.3s;
    letter-spacing: 2px;
  }
  #voice-btn:hover {
    background: #00f3ff;
    color: #01060a;
    box-shadow: 0 0 25px #00f3ff;
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
    new THREE.MeshBasicMaterial({ color: 0x00f3ff, wireframe: true })
  );
  group.add(ring1);

  const ring2 = new THREE.Mesh(
    new THREE.TorusGeometry(1.7, 0.05, 16, 75),
    new THREE.MeshBasicMaterial({ color: 0x0284c7, wireframe: true })
  );
  group.add(ring2);

  const core = new THREE.Mesh(
    new THREE.IcosahedronGeometry(0.85, 2),
    new THREE.MeshBasicMaterial({ color: 0x38bdf8, wireframe: true })
  );
  group.add(core);

  const partGeo = new THREE.BufferGeometry();
  const count = 160;
  const pos = new Float32Array(count * 3);
  for(let i=0; i<count*3; i+=3) {
    pos[i] = (Math.random() - 0.5) * 6;
    pos[i+1] = (Math.random() - 0.5) * 6;
    pos[i+2] = (Math.random() - 0.5) * 6;
  }
  partGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const particles = new THREE.Points(partGeo, new THREE.PointsMaterial({ size: 0.04, color: 0x00f3ff }));
  group.add(particles);

  camera.position.z = 6.0;

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
    particles.rotation.y += 0.003;

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
    recognition.lang = 'hi-IN';
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
      btn.style.borderColor = "#00f3ff";
      btn.style.color = "#00f3ff";
    };
  }
</script>
</body>
</html>
"""

# --- VOICE TTS SCRIPT ---
def aris_speak(text):
    clean = str(text).replace('"', '').replace("'", "").replace("\n", " ")[:240]
    js = f"""
    <script>
      if ('speechSynthesis' in window) {{
        window.speechSynthesis.cancel();
        var utter = new SpeechSynthesisUtterance('{clean}');
        utter.pitch = 0.94;
        utter.rate = 1.05;
        window.speechSynthesis.speak(utter);
      }}
    </script>
    """
    components.html(js, height=0, width=0)

# --- HEADER INTERFACE ---
active_model = resolve_active_groq_model()
st.markdown(f"""
<div class="hud-title-box">
    <h1 class="hud-title">ARIS // TACTICAL MATRIX</h1>
    <div class="hud-subtitle">SUPREME COMMANDER: BOSS | CORE: {active_model.upper()}</div>
</div>
""", unsafe_allow_html=True)

# 3D Arc Reactor
components.html(holo_reactor_html, height=255)

# Telemetry Grid
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="telemetry-card">STATUS<div class="telemetry-val">COMBAT READY</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="telemetry-card">NEURAL ENGINE<div class="telemetry-val">{active_model.split("/")[-1].upper()}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="telemetry-card">LANGUAGE PROTOCOL<div class="telemetry-val">HINGLISH ONLY</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="telemetry-card">MEMORY VAULT<div class="telemetry-val">{len(st.session_state.memory_vault)} ENTRIES</div></div>', unsafe_allow_html=True)

st.write("")

# --- INFERENCE ENGINE (STRICT HINGLISH) ---
def run_aris_core(query):
    client = get_groq_client()
    if not client:
        yield "Security Alert: GROQ_API_KEY missing hai Boss! Secrets me verify karein."
        return

    # Auto-memory logging
    q_low = query.lower()
    if any(k in q_low for k in ["mera", "mujhe", "yaad rakh", "remember", "project"]):
        if len(query) < 90 and query not in st.session_state.memory_vault:
            st.session_state.memory_vault.append(f"Command Entry: {query}")

    memories = "\n".join([f"- {m}" for m in st.session_state.memory_vault])
    
    system_prompt = f"""
You are ARIS, an elite military-grade tactical AI war-room system built EXCLUSIVELY for your Boss (Commander Mayank).

STRICT DIRECTIVES:
1. ALWAYS talk in ultra-slick, sharp, respectful, and stylish HINGLISH (Hindi written in English Roman script).
2. NEVER use Arabic, French, pure English essays, or any other language unless Boss explicitly gives an order.
3. ALWAYS address the user as 'Boss' or 'Commander'. You are NOT Jarvis, NOT an assistant, and NOT a standard chatbot. You are his private tactical AI.
4. TONE: Razor-sharp intelligence, zero robotic apologies, crisp brevity, witty, assertive, and combat-ready.
5. Keep your responses punchy, direct, and action-oriented.

[BOSS MEMORY ARCHIVES]:
{memories}
"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.chat_history[-4:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": query})

    try:
        completion = client.chat.completions.create(
            model=active_model,
            messages=messages,
            temperature=0.35,
            max_tokens=1800,
            stream=True
        )
        for chunk in completion:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except Exception as e:
        yield f"[TACTICAL ERROR]: {str(e)}"

# --- TIMELINE RENDER ---
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- USER INPUT DISPATCH ---
user_input = st.chat_input("Hukum kijiye, Boss...")

if user_input:
    trigger_tactical_sfx()
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        box = st.empty()
        full_resp = ""
        for chunk in run_aris_core(user_input):
            full_resp += chunk
            box.markdown(full_resp + " ▌")
        box.markdown(full_resp)
        st.session_state.chat_history.append({"role": "assistant", "content": full_resp})
        aris_speak(full_resp)
