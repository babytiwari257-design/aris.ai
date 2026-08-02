import streamlit as st
from groq import Groq
import base64
from streamlit_mic_recorder import mic_recorder
import sqlite3
from duckduckgo_search import DDGS
import uuid

# --- PAGE CONFIGURATION & MODERN COOL THEME ---
st.set_page_config(
    page_title="ARIS V3 - ARIS Industries", 
    page_icon="⚡",
    layout="centered"
)

# --- TARGETED PRIVACY: HIDE GITHUB/FORK ONLY, KEEP SIDEBAR & CONTROLS INTACT ---
hide_github_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Hide only the top-right GitHub icon and fork elements */
    [data-testid="stToolbar"] {
        display: none !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
        visibility: visible !important;
    }
    </style>
"""
st.markdown(hide_github_style, unsafe_allow_html=True)

# Custom Styling for a Cool, Sleek Look
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #030712 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    .main-header {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(56, 189, 248, 0.2);
        padding: 20px 25px;
        border-radius: 14px;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.1);
        margin-bottom: 25px;
        backdrop-filter: blur(10px);
    }
    .stChatMessage {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 12px;
        backdrop-filter: blur(5px);
    }
    section[data-testid="stSidebar"] {
        background-color: #0b0f19;
        border-right: 1px solid rgba(56, 189, 248, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 26px; background: linear-gradient(45deg,
