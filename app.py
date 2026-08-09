import streamlit as st
import os
import subprocess
from groq import Groq

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ARIS V15.0 // Enterprise Neural Core",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CYBERPUNK / JARVIS CSS STYLING ---
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    /* Sidebar Styling */
    css-1d391kg, [data-testid="stSidebar"] {
        background-color: #07090e;
        border-right: 1px solid #1e293b;
    }
    /* Custom Headers */
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
    /* Card Styling */
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

# --- INITIALIZE SESSION STATES ---
if "threads" not in st.session_state:
    st.session_state.threads = {"Desktop Protocol": []}

if "current_thread" not in st.session_state:
    st.session_state.current_thread = "Desktop Protocol"

if "memory_vault" not in st.session_state:
    st.session_state.memory_vault = []

# --- SIDEBAR COMMAND CENTER ---
with st.sidebar:
    st.markdown("### 🎛️ ARIS Command Center")
    
    # 1. New Thread Creation
    new_thread_name = st.text_input("Thread Name", placeholder="e.g., Project Omega...")
    if st.button("➕ Create Neural Thread", use_container_width=True):
        if new_thread_name and new_thread_name not in st.session_state.threads:
            st.session_state.threads[new_thread_name] = []
            st.session_state.current_thread = new_thread_name
            st.rerun()

    st.markdown("---")
    
    # 2. Interactive Chat History / Threads Selector (Click to Open!)
    st.markdown("💬 **Active Threads & History**")
    for thread_name in list(st.session_state.threads.keys()):
        if st.button(f"📂 {thread_name}", use_container_width=True, key=f"thread_{thread_name}"):
            st.session_state.current_thread = thread_name
            st.rerun()

    st.markdown("---")
    
    # 3. Long-Term Memory Vault (Clickable/Viewable Saved Memory)
    st.markdown("🧠 **Memory Vault**")
    if not st.session_state.memory_vault:
        st.caption("Vault empty. Use 'remember [fact]' in chat.")
    else:
        for idx, mem in enumerate(st.session_state.memory_vault):
            st.info(f"🔹 {mem}")

    st.markdown("---")
    
    # 4. Purge Session Button
    if st.button("🗑️ Purge Active Session", use_container_width=True, type="primary"):
        st.session_state.threads[st.session_state.current_thread] = []
        st.rerun()

# --- MAIN CHAT INTERFACE ---
st.markdown(f"""
<div class="aris-header">
    <h2>⚡ ARIS AI ASSISTANT // CORE V15.0</h2>
    <p style="margin:0; font-size:13px; color:#fca5a5;">SYSTEM ARCHITECT: MAYANK | ACTIVE THREAD: {st.session_state.current_thread}</p>
</div>
""", unsafe_allow_html=True)

# Top Status Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="metric-card"><b>MODEL</b><br>LLaMA-3.3 70B</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><b>AUTOMATION</b><br>Desktop Enabled</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><b>VECTOR VAULT</b><br>Synced</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-card"><b>SECURITY</b><br>Encrypted</div>', unsafe_allow_html=True)

st.write("")

# Display Current Thread Messages
current_messages = st.session_state.threads[st.session_state.current_thread]

for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input
user_query = st.chat_input("Enter command, query, or desktop automation code...")

if user_query:
    # Append user message to active thread
    current_messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Process AI Response & Memory/Automation triggers
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("⚡ *Processing neural request...*")
        
        q_lower = user_query.lower()
        
        # Memory saving trigger
        if q_lower.startswith("remember "):
            fact = user_query[9:].strip()
            st.session_state.memory_vault.append(fact)
            response = f"Memory successfully stored in Vault: '{fact}'"
        # Desktop automation shortcuts
        elif "open notepad" in q_lower:
            try:
                subprocess.Popen(["notepad.exe"])
                response = "Executing protocol: Notepad launched successfully, Boss Mayank."
            except Exception as e:
                response = f"Error launching notepad: {str(e)}"
        elif "open chrome" in q_lower or "open browser" in q_lower:
            try:
                os.system("start chrome")
                response = "Executing protocol: Web browser launched."
            except Exception as e:
                response = f"Error launching browser: {str(e)}"
        else:
            # Groq AI Call
            try:
                client = Groq(api_key=os.environ.get("GROQ_API_KEY") or "YOUR_GROQ_API_KEY")
                system_prompt = (
                    "You are ARIS, an elite AI Desktop Assistant modeled after JARVIS, "
                    "engineered exclusively by Mayank. Reply in natural, conversational Hinglish "
                    "with a sharp, techy, and friendly tone."
                )
                
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_query}
                    ]
                )
                response = completion.choices[0].message.content
            except Exception as e:
                response = f"Neural link error: Make sure Groq API key is configured. Details: {str(e)}"

        message_placeholder.markdown(response)
        current_messages.append({"role": "assistant", "content": response})
