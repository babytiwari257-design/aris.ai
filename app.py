import streamlit as st
import os
import subprocess
from groq import Groq

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ARIS // Master Neural Core",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CYBERPUNK STYLING ---
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    .aris-header {
        background: linear-gradient(90deg, #dc2626 0%, #7f1d1d 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-weight: 800;
        letter-spacing: 2px;
        box-shadow: 0 4px 20px rgba(220, 38, 38, 0.4);
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        color: #f3f4f6;
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
    clean_text = text.replace('"', '').replace("'", "").replace("\n", " ")
    js_code = f"""
    <script>
        var msg = new SpeechSynthesisUtterance('{clean_text}');
        msg.rate = 1.0;
        msg.pitch = 0.9;
        window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)

# --- AGENT 2: 'OMEGA' (Graphics & Desktop Automation Unit) ---
def omega_graphics_desktop_agent(query):
    q_lower = query.lower()
    if "open notepad" in q_lower:
        try:
            subprocess.Popen(["notepad.exe"])
            return "OMEGA (Graphics/Desktop Unit): Notepad successfully launched."
        except Exception as e:
            return f"OMEGA Error: {str(e)}"
    elif "open chrome" in q_lower or "open browser" in q_lower:
        try:
            os.system("start chrome")
            return "OMEGA (Graphics/Desktop Unit): Web browser initiated."
        except Exception as e:
            return f"OMEGA Error: {str(e)}"
    elif "shutdown pc" in q_lower:
        os.system("shutdown /s /t 5")
        return "WARNING! OMEGA Security Unit triggered system shutdown."
    return None

# --- AGENT 3: 'HELIOS' (Chat Manager & Memory Unit) ---
def helios_chat_memory_agent(query):
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY") or "YOUR_GROQ_API_KEY")
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
def aris_master_controller(query):
    q_lower = query.lower()
    
    # Check if Helios Memory Vault action is needed
    if q_lower.startswith("remember "):
        fact = query[9:].strip()
        st.session_state.memory_vault.append(fact)
        return f"ARIS (Master Boss): Helios has successfully recorded this in the Memory Vault: '{fact}'"
        
    # Check if Omega Graphics/Desktop action is needed
    omega_result = omega_graphics_desktop_agent(query)
    if omega_result:
        return f"ARIS (Master Boss): Task delegated to OMEGA -> {omega_result}"
        
    # Default: Delegate to Helios Chat Manager
    helios_response = helios_chat_memory_agent(query)
    return f"ARIS (Master Boss Core): {helios_response}"

# --- SIDEBAR CONTROL DECK ---
with st.sidebar:
    st.markdown("### 🎛️ ARIS COMMAND CENTER")
    new_thread = st.text_input("Thread Name", placeholder="e.g., Operation Alpha...")
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
    <h2>⚡ ARIS // SUPREME MASTER CORE</h2>
    <p style="margin:0; font-size:13px; color:#fca5a5;">MASTER BOSS: ARIS | ACTIVE THREAD: {st.session_state.current_thread}</p>
</div>
""", unsafe_allow_html=True)

# Metrics Grid showing the Squad
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="metric-card"><b>MASTER BOSS</b><br>ARIS</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><b>CHAT & MEMORY</b><br>HELIOS</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><b>GRAPHICS & DESKTOP</b><br>OMEGA</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-card"><b>VOICE UNIT</b><br>MJ</div>', unsafe_allow_html=True)

st.write("")

# Chat Display
current_messages = st.session_state.threads[st.session_state.current_thread]
for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Query Input
user_query = st.chat_input("Command Master ARIS and his squad...")

if user_query:
    current_messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("⚡ *ARIS is coordinating with Helios, Omega, and MJ...*")
        
        # Master Boss ARIS orchestrates everything
        final_response = aris_master_controller(user_query)
            
        placeholder.markdown(final_response)
        current_messages.append({"role": "assistant", "content": final_response})
        
        # Trigger Voice Unit 'MJ' to speak out the response
        mj_voice_agent(final_response)
