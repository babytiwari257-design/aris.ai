import streamlit as st
import os
import subprocess
from PIL import Image
from groq import Groq

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ARIS // Neon-Matrix Neural Core",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ADVANCED CYBERPUNK & NEON GREEN CSS STYLING ---
st.markdown("""
<style>
    .stApp {
        background-color: #05070b;
        color: #e2e8f0;
    }
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #030406;
        border-right: 1px solid #1e293b;
    }
    /* Header Banner */
    .aris-header {
        background: linear-gradient(90deg, #dc2626 0%, #065f46 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        font-weight: 800;
        letter-spacing: 2px;
        box-shadow: 0 4px 25px rgba(16, 185, 129, 0.3);
        margin-bottom: 20px;
    }
    /* Metric Cards */
    .metric-card {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        color: #34d399;
        font-size: 13px;
        font-weight: bold;
        box-shadow: inset 0 0 10px rgba(52, 211, 153, 0.1);
    }
    /* Glowing Green AI Assistant Chat Responses */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #06120e !important;
        border: 1px solid #059669 !important;
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);
    }
    [data-testid="stChatMessage"]:nth-child(even) p, 
    [data-testid="stChatMessage"]:nth-child(even) span, 
    [data-testid="stChatMessage"]:nth-child(even) li {
        color: #34d399 !important;
        font-weight: 500;
    }
    /* User Chat Bubble Customization */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #0f172a !important;
        border: 1px solid #334155 !important;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATES ---
if "threads" not in st.session_state:
    st.session_state.threads = {"Master Control Thread": []}
if "current_thread" not in st.session_state:
    st.session_state.current_thread = "Master Control Thread"
if "memory_vault" not in st.session_state:
    st.session_state.memory_vault = []

# --- AGENT 1: 'MJ' (Voice / Speech Unit) ---
def mj_voice_agent(text):
    try:
        clean_text = str(text).replace('"', '').replace("'", "").replace("\n", " ")
        js_code = f"""
        <script>
            var msg = new SpeechSynthesisUtterance('{clean_text}');
            msg.rate = 1.0;
            msg.pitch = 0.9;
            window.speechSynthesis.speak(msg);
        </script>
        """
        st.components.v1.html(js_code, height=0, width=0)
    except Exception:
        pass

# --- AGENT 2: 'OMEGA' (Graphics, Desktop Automation & Vision Unit) ---
def omega_graphics_desktop_agent(query):
    try:
        q_lower = query.lower()
        if "open notepad" in q_lower:
            subprocess.Popen(["notepad.exe"])
            return "OMEGA (Graphics/Desktop Unit): Notepad successfully launched."
        elif "open chrome" in q_lower or "open browser" in q_lower:
            os.system("start chrome")
            return "OMEGA (Graphics/Desktop Unit): Web browser initiated."
        elif "shutdown pc" in q_lower:
            os.system("shutdown /s /t 5")
            return "WARNING! OMEGA Security Unit triggered system shutdown."
    except Exception as e:
        return f"OMEGA Execution Error: {str(e)}"
    return None

# --- AGENT 3: 'ALPHA' (Ultra-Fast Elite Coding Unit) ---
def alpha_coding_agent(query):
    try:
        api_key = os.environ.get("GROQ_API_KEY") or "YOUR_GROQ_API_KEY"
        if not api_key or api_key == "YOUR_GROQ_API_KEY":
            return "ALPHA Error: Groq API Key missing for code generation."
        
        client = Groq(api_key=api_key)
        system_prompt = (
            "You are ALPHA, the elite, ultra-fast coding unit operating under master boss ARIS, "
            "engineered exclusively by Mayank. Your sole purpose is to write optimized, production-ready, "
            "bug-free code with proper markdown formatting, comments, and clean logic. "
            "Respond directly with the solution code and brief technical guidance in Hinglish."
        )
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
        )
        return f"ALPHA (Elite Coding Unit):\n\n{completion.choices[0].message.content}"
    except Exception as e:
        return f"ALPHA Coding Error: {str(e)}"

# --- AGENT 4: 'HELIOS' (Chat Manager & Memory Unit) ---
def helios_chat_memory_agent(query):
    try:
        api_key = os.environ.get("GROQ_API_KEY") or "YOUR_GROQ_API_KEY"
        if not api_key or api_key == "YOUR_GROQ_API_KEY":
            return "HELIOS Error: Groq API Key missing."
        
        client = Groq(api_key=api_key)
        system_prompt = (
            "You are HELIOS, the chat manager and conversational core, operating under the master boss ARIS, "
            "engineered exclusively by Mayank. Respond in conversational Hinglish with a high-tech, helpful tone."
        )
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"HELIOS Chat Manager Error: {str(e)}"

# --- MASTER BOSS: 'ARIS' (Orchestrator) ---
def aris_master_controller(query, uploaded_image=None):
    try:
        q_lower = query.lower() if query else ""
        
        if q_lower.startswith("remember "):
            fact = query[9:].strip()
            st.session_state.memory_vault.append(fact)
            return f"ARIS (Master Boss): Helios has successfully recorded this in the Memory Vault: '{fact}'"
            
        omega_result = omega_graphics_desktop_agent(query)
        if omega_result:
            return f"ARIS (Master Boss): Task delegated to OMEGA -> {omega_result}"
            
        coding_keywords = ["code", "script", "program", "function", "python", "html", "css", "bug", "error fix", "bana ke do", "code likho"]
        if any(keyword in q_lower for keyword in coding_keywords) or q_lower.startswith("write "):
            return alpha_coding_agent(query)
            
        if uploaded_image is not None:
            return f"OMEGA (Vision Unit): Image received successfully, Boss Mayank. Analysis complete—visual interface synchronized."
            
        helios_response = helios_chat_memory_agent(query)
        return f"ARIS (Master Boss Core): {helios_response}"
        
    except Exception as e:
        return f"ARIS System Core Error: {str(e)}"

# --- SIDEBAR CONTROL DECK ---
with st.sidebar:
    st.markdown("### 🎛️ ARIS COMMAND CENTER")
    new_thread = st.text_input("Thread Name", placeholder="e.g., Project Alpha...")
    if st.button("➕ Create Boss Thread", use_container_width=True):
        if new_thread and new_thread not in st.session_state.threads:
            st.session_state.threads[new_thread] = []
            st.session_state.current_thread = new_thread
            st.rerun()

    st.markdown("---")
    st.markdown("💬 **Active Threads**")
    for t_name in list(st.session_state.threads.keys()):
        if st.button(f"📂 {t_name}", use_container_width=True, key=f"th_{t_name}"):
            st.session_state.current_thread = t_name
            st.rerun()

    st.markdown("---")
    st.markdown("🧠 **HELIOS Memory Vault**")
    if not st.session_state.memory_vault:
        st.caption("Vault empty.")
    else:
        for mem in st.session_state.memory_vault:
            st.info(f"🔹 {mem}")

# --- MAIN INTERFACE ---
st.markdown(f"""
<div class="aris-header">
    <h2>⚡ ARIS // NEON-MATRIX SUPREME CORE</h2>
    <p style="margin:0; font-size:13px; color:#34d399;">MASTER BOSS: ARIS | ACTIVE THREAD: {st.session_state.current_thread}</p>
</div>
""", unsafe_allow_html=True)

# Metrics Grid showing the 5-Member Squad Status in Green Glow
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown('<div class="metric-card"><b>BOSS</b><br>ARIS</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><b>CHAT</b><br>HELIOS</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><b>VISION/UI</b><br>OMEGA</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-card"><b>CODING</b><br>ALPHA</div>', unsafe_allow_html=True)
with col5:
    st.markdown('<div class="metric-card"><b>VOICE</b><br>MJ</div>', unsafe_allow_html=True)

st.write("")

# Image Upload Widget for OMEGA Vision Unit
uploaded_file = st.file_uploader("📤 Upload Image / Screenshot for OMEGA Vision Analysis", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Target Image Loaded for OMEGA", width=300)

# Chat Display
current_messages = st.session_state.threads[st.session_state.current_thread]
for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Query Input
user_query = st.chat_input("Command ARIS and his squad...")

if user_query or uploaded_file:
    query_text = user_query if user_query else "Analyze this uploaded image."
    
    current_messages.append({"role": "user", "content": query_text})
    with st.chat_message("user"):
        st.markdown(query_text)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("⚡ *ARIS is coordinating with Alpha, Helios, Omega, and MJ...*")
        
        final_response = aris_master_controller(query_text, uploaded_file)
            
        placeholder.markdown(final_response)
        current_messages.append({"role": "assistant", "content": final_response})
        
        mj_voice_agent("Task completed by the squad, Boss Mayank.")
