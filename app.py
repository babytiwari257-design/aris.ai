import streamlit as st
import streamlit.components.v1 as components
import os
import json
from groq import Groq

# --- MATRIX CONFIGURATION ---
st.set_page_config(
    page_title="ARIS // TACTICAL COMMAND",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ULTIMATE OLED OBSIDIAN GLASS HUD ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;700;800;900&family=Rajdhani:wght@500;600;700&display=swap');

    .stApp {
        background: 
            radial-gradient(circle at 50% 0%, rgba(0, 229, 255, 0.08) 0%, transparent 60%),
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
        background: rgba(9, 20, 36, 0.85);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(0, 229, 255, 0.5);
        border-radius: 14px;
        padding: 16px 28px;
        text-align: center;
        box-shadow: 
            0 0 25px rgba(0, 229, 255, 0.18),
            inset 0 0 15px rgba(0, 229, 255, 0.06);
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
    .telemetry-card:hover {
        border-color: #00e5ff;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.2);
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
        margin-bottom: 12px !important;
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

    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] li, 
    [data-testid="stChatMessage"] span {
        color: #f8fafc !important;
    }
    [data-testid="stChatMessage"] strong {
        color: #00e5ff !important;
        text-shadow: 0 0 8px rgba(0, 229, 255, 0.4) !important;
    }

    pre, code {
        background-color: #020617 !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
        border-radius: 8px !important;
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

# --- LIVE METALLIC "A" INSIGNIA WITH ROTATING ARCS & PARTICLES ---
aris_hologram_core_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; overflow: hidden; background: transparent; display: flex; justify-content: center; align-items: center; }
  #hologram-stage {
    position: relative;
    width: 100%;
    height: 270px;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  /* Outer Ambient Cyan Orbit */
  .energy-ring-outer {
    position: absolute;
    width: 250px;
    height: 250px;
    border-radius: 50%;
    border: 1px dashed rgba(0, 229, 255, 0.35);
    box-shadow: 0 0 30px rgba(0, 229, 255, 0.15);
    animation: spinClockwise 22s linear infinite;
  }

  /* Mid Segmented Gyro Ring */
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

  /* Logo Shield Node */
  .logo-core {
    position: relative;
    width: 175px;
    height: 175px;
    border-radius: 50%;
    background: radial-gradient(circle, #071526 30%, #030a14 80%, #010408 100%);
    box-shadow: 
      0 0 40px rgba(0, 229, 255, 0.6),
      inset 0 0 25px rgba(0, 229, 255, 0.4);
    border: 2px solid rgba(0, 229, 255, 0.7);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    animation: reactorPulse 3.5s ease-in-out infinite;
    transform-style: preserve-3d;
    transition: transform 0.1s ease-out;
    cursor: pointer;
  }

  /* Built-in High Precision Metallic "A" Insignia */
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

  @keyframes spinClockwise {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  @keyframes spinCounter {
    from { transform: rotate(0deg); }
    to { transform: rotate(-360deg); }
  }
  @keyframes reactorPulse {
    0%, 100% {
      transform: scale(1);
      box-shadow: 0 0 35px rgba(0, 229, 255, 0.5), inset 0 0 18px rgba(0, 229, 255, 0.35);
    }
    50% {
      transform: scale(1.03);
      box-shadow: 0 0 55px rgba(0, 229, 255, 0.85), inset 0 0 28px rgba(0, 229, 255, 0.6);
    }
  }
  @keyframes circuitPulse {
    0%, 100% { opacity: 0.9; }
    50% { opacity: 1; filter: drop-shadow(0 0 16px rgba(0, 229, 255, 1)); }
  }

  #voice-btn {
    position: absolute;
    bottom: 4px;
    background: rgba(9, 24, 44, 0.85);
    border: 1px solid #00e5ff;
    color: #00e5ff;
    font-family: 'Orbitron', sans-serif;
    font-size: 11px;
    font-weight: 700;
    padding: 7px 22px;
    border-radius: 24px;
    cursor: pointer;
    box-shadow: 0 0 15px rgba(0, 229, 255, 0.35);
    transition: all 0.25s ease;
    letter-spacing: 1.5px;
  }
  #voice-btn:hover {
    background: #00e5ff;
    color: #030712;
    box-shadow: 0 0 25px #00e5ff;
  }
</style>
</head>
<body>
<div id="hologram-stage">
  <div class="energy-ring-outer"></div>
  <div class="energy-ring-inner"></div>
  
  <div class="logo-core" id="logoBox">
    <!-- Precision Vector "A" Insignia with Internal Circuits -->
    <svg class="insignia-svg" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="metallicChrome" x1="
