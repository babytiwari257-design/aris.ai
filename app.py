import streamlit as st
import os
import subprocess
from PIL import Image
from groq import Groq
import base64

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ARIS // Vision-Matrix Supreme Core",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ADVANCED CYBERPUNK & NEON BLUE/GREEN CSS STYLING ---
st.markdown("""
<style>
    .stApp {
        background-color: #05070b;
        color: #e2e8f0;
    }
    [data-testid="stSidebar"] {
        background-color: #030406;
        border-right: 1px solid #1e293b;
    }
    .aris-header {
        background: linear-gradient(90deg, #dc2626 0%, #0284c7 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        font-weight: 800;
        letter-spacing: 2px;
        box-shadow: 0 4px 25px rgba(2, 132, 199, 0.3);
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #0f172a;
        border: 1px solid #1f2937;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        color: #38bdf8;
        font-size: 13px;
        font-weight: bold;
        box-shadow: inset 0 0 10px rgba(56, 189, 248, 0.1);
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
    /* Neon Blue User Chat Bubbles */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #082f49 !important;
        border: 1px solid #0284c7 !important;
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(2, 132, 199, 0.2);
    }
    [data-testid="stChatMessage"]:nth-child(odd) p, 
    [data-testid="stChatMessage"]:nth-child(odd) span, 
    [data-testid="stChatMessage"]:nth-child(odd) li {
        color: #38bdf8 !important;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# --- CLIENT CACHE ---
@st.cache_resource
def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

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
        if len(clean_text) > 250:
            clean_text = clean_text[:250] + " ... response continues on screen."
        js_code = f"""
        <script>
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance('{clean_text}');
                msg.rate = 1.0;
                msg.pitch = 0.9;
                window.speechSynthesis.speak(msg);
            }}
        </script>
        """
        st.components.v1.html(js_code, height=0, width=0)
    except Exception:
        pass

# --- AGENT 2: 'OMEGA' (Graphics & Desktop Unit) ---
def omega_graphics_desktop_agent(query):
    try:
        q_lower = query.lower()
        if "open notepad" in q_lower:
            subprocess.Popen(["notepad.exe"])
            return "OMEGA: Notepad successfully launched on your system, Boss."
        elif "open chrome" in q_lower or "open browser" in q_lower:
            os.system("start chrome")
            return "OMEGA: Web browser initiated successfully."
        elif "shutdown pc" in q_lower:
            os.system("shutdown /s /t 5")
            return "WARNING! OMEGA Security Unit triggered system shutdown."
    except Exception as e:
        return f"OMEGA Execution Error: {str(e)}"
    return None

# --- AGENT 3: 'OMEGA VISION' (Active Vision Model) ---
def omega_vision_agent(query, uploaded_file, lang_instruction):
    try:
        client = get_groq_client()
        if not client:
            return "OMEGA Vision Error: Missing GROQ_API_KEY environment variable."

        bytes_data = uploaded_file.getvalue()
        base64_image = base64.b64encode(bytes_data).decode('utf-8')
        
        img_type = uploaded_file.type.split("/")[-1].lower()
        if img_type not in ["jpeg", "png", "jpg", "webp"]:
            img_type = "jpeg"

        system_prompt = (
            f"You are OMEGA, the elite vision unit operating under master boss ARIS, engineered by Mayank. "
            f"Analyze the visual input accurately and answer the question in detail. {lang_instruction}"
        )
        
        model_name = "llama-3.2-11b-vision-instant"

        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"{system_prompt}\n\nTask: {query}"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{img_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.4,
            max_tokens=1024
        )
        return f"OMEGA (Vision Unit - {model_name}):\n\n{completion.choices[0].message.content}"
    except Exception as e:
        return f"OMEGA Vision Error: {str(e)}"

# --- AGENT 4: 'ALPHA' (Coding Unit) ---
def alpha_coding_agent(query, user_lang_instruction):
    try:
        client = get_groq_client()
        if not client:
            return "ALPHA Error: Missing GROQ_API_KEY environment variable."

        system_prompt = (
            f"You are ALPHA, an elite coding unit under master boss ARIS, engineered by Mayank. "
            f"Write robust, optimized, and cleanly structured code. {user_lang_instruction}"
        )
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.2
        )
        return f"ALPHA (Elite Coding Unit):\n\n{completion.choices[0].message.content}"
    except Exception as e:
        return f"ALPHA Coding Error: {str(e)}"

# --- AGENT 5: 'HELIOS' (Chat Manager with Dynamic Memory Vault Injection) ---
def helios_chat_memory_agent(query, user_lang_instruction):
    try:
        client = get_groq_client()
        if not client:
            return "HELIOS Error: Missing GROQ_API_KEY environment variable."

        # Compile persistent memories stored in the vault
        memory_vault = st.session_state.get("memory_vault", [])
        if memory_vault:
            formatted_memories = "\n".join([f"- {fact}" for fact in memory_vault])
            memory_context = (
                f"\n\n[MEMORY VAULT - PERSISTENT CONTEXT]:\n"
                f"You have access to the following saved user facts in your memory bank. "
                f"Seamlessly incorporate and acknowledge these facts whenever relevant:\n"
                f"{formatted_memories}\n"
            )
        else:
            memory_context = "\n\n[MEMORY VAULT]: Empty (No prior user facts recorded)."

        system_prompt = (
            f"You are HELIOS, chat manager operating under master boss ARIS, engineered by Mayank. "
            f"{user_lang_instruction}"
            f"{memory_context}"
        )

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"HELIOS Chat Manager Error: {str(e)}"

# --- MASTER BOSS: 'ARIS' (Orchestrator) ---
def aris_master_controller(query, uploaded_image=None):
    try:
        q_lower = query.lower() if query else ""
        
        hindi_keywords = ["kya", "kaise", "batao", "likho", "hain", "hai", "kaun", "karo", "yeh", "woh", "mujhe", "mera", "dekho"]
        is_hindi = any(word in q_lower for word in hindi_keywords) or any(ord(c) > 127 for c in query)
        
        if is_hindi:
            lang_instruction = "User is communicating in Hindi/Hinglish. You MUST reply strictly in conversational Hinglish/Hindi with a smart techy tone."
        else:
            lang_instruction = "User is communicating in English. Reply in clear, professional English."

        # Recording logic for "remember ..."
        if q_lower.startswith("remember "):
            fact = query[9:].strip()
            if fact and fact not in st.session_state.memory_vault:
                st.session_state.memory_vault.append(fact)
            return (
                f"ARIS (Master Boss): Helios ne yeh memory vault mein successfully inject kar liya hai: '{fact}'" 
                if is_hindi else 
                f"ARIS (Master Boss): Helios has permanently indexed this fact in the Memory Vault: '{fact}'"
            )
            
        omega_result = omega_graphics_desktop_agent(query)
        if omega_result:
            return omega_result
            
        if uploaded_image is not None:
            return omega_vision_agent(query, uploaded_image, lang_instruction)
            
        coding_keywords = ["code", "script", "program", "function", "python", "html", "css", "bug", "error", "bana ke do", "likho"]
        if any(keyword in q_lower for keyword in coding_keywords) or q_lower.startswith("write "):
            return alpha_coding_agent(query, lang_instruction)
            
        return helios_chat_memory_agent(query, lang_instruction)
        
    except Exception as e:
        return f"ARIS System Core Error: {str(e)}"

# --- SIDEBAR CONTROL DECK ---
with st.sidebar:
    st.markdown("### 🎛️ ARIS COMMAND CENTER")
    
    new_thread = st.text_input("Thread Name", placeholder="e.g., Project Alpha...")
    if st.button("➕ New Neural Thread", use_container_width=True):
        if new_thread and new_thread not in st.session_state.threads:
            st.session_state.threads[new_thread] = []
            st.session_state.current_thread = new_thread
            st.rerun()

    if st.button("🗑️️ Purge Active Session", use_container_width=True):
        st.session_state.threads[st.session_state.current_thread] = []
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
        st.caption("Vault empty. Command 'remember <fact>' to persist data.")
    else:
        for idx, mem in enumerate(st.session_state.memory_vault):
            col_mem, col_del = st.columns([5, 1])
            with col_mem:
                st.info(f"🔹 {mem}")
            with col_del:
                if st.button("✖", key=f"del_mem_{idx}"):
                    st.session_state.memory_vault.pop(idx)
                    st.rerun()

# --- MAIN INTERFACE ---
st.markdown(f"""
<div class="aris-header">
    <h2>⚡ ARIS // VISION-MATRIX SUPREME CORE</h2>
    <p style="margin:0; font-size:13px; color:#38bdf8;">MASTER BOSS: ARIS | ACTIVE THREAD: {st.session_state.current_thread}</p>
</div>
""", unsafe_allow_html=True)

# Metrics Grid
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown('<div class="metric-card"><b>BOSS</b><br>ARIS</div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><b>CHAT</b><br>HELIOS ({len(st.session_state.memory_vault)} facts)</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><b>VISION</b><br>OMEGA (Vision Inst.)</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-card"><b>CODING</b><br>ALPHA (Llama 3.3)</div>', unsafe_allow_html=True)
with col5:
    st.markdown('<div class="metric-card"><b>VOICE</b><br>MJ</div>', unsafe_allow_html=True)

st.write("")

# Image Upload Widget
uploaded_file = st.file_uploader("📤 Upload Image / Screenshot for OMEGA Vision Analysis", type=["jpg", "jpeg", "png", "webp"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Target Image Loaded for OMEGA Vision", width=300)

# Chat Display
current_messages = st.session_state.threads[st.session_state.current_thread]
for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Query Input
user_query = st.chat_input("Command ARIS and his squad...")

if user_query or (uploaded_file and len(current_messages) == 0):
    query_text = user_query if user_query else "Analyze this uploaded image and explain it."
    
    current_messages.append({"role": "user", "content": query_text})
    with st.chat_message("user"):
        st.markdown(query_text)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("⚡ *ARIS is coordinating with Alpha, Helios, Omega (Vision), and MJ...*")
        
        final_response = aris_master_controller(query_text, uploaded_file)
            
        placeholder.markdown(final_response)
        current_messages.append({"role": "assistant", "content": final_response})
        
        mj_voice_agent(final_response)
