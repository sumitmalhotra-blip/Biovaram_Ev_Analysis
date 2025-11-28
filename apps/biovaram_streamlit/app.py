# app.py

import streamlit as st
import os
import io
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import base64

# Import API client
from api_client import get_client, check_api_connection

# Optional libraries
use_pymiescatt = False
try:
    import PyMieScatt as PMS  # type: ignore[import-not-found]
    use_pymiescatt = True
except Exception:
    use_pymiescatt = False

use_fcsparser = False
try:
    import fcsparser  # type: ignore[import-not-found]
    use_fcsparser = True
except Exception:
    use_fcsparser = False

use_pyarrow = False
try:
    import pyarrow as pa  # type: ignore[import-not-found]
    import pyarrow.parquet as pq  # type: ignore[import-not-found]
    use_pyarrow = True
except Exception:
    use_pyarrow = False

# Streamlit config
st.set_page_config(
    page_title="EV Analysis Tool",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure directories
os.makedirs("images", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

# =================================================================================
# ENHANCED CSS STYLING - COMPLETE PROFESSIONAL THEME
# =================================================================================
st.markdown("""
<style>
    /* ========== GOOGLE FONTS ========== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ========== CSS VARIABLES ========== */
    :root {
        --primary: #00b4d8;
        --primary-dark: #0096c7;
        --primary-light: #48cae4;
        --primary-glow: rgba(0, 180, 216, 0.4);
        --secondary: #7c3aed;
        --secondary-light: #a78bfa;
        --secondary-glow: rgba(124, 58, 237, 0.3);
        --accent: #f72585;
        --accent-light: #ff6b9d;
        --success: #10b981;
        --success-bg: rgba(16, 185, 129, 0.15);
        --warning: #f59e0b;
        --warning-bg: rgba(245, 158, 11, 0.15);
        --error: #ef4444;
        --error-bg: rgba(239, 68, 68, 0.15);
        --info-bg: rgba(0, 180, 216, 0.15);
        --bg-dark: #0a0e17;
        --bg-darker: #060910;
        --bg-card: #111827;
        --bg-card-hover: #1f2937;
        --bg-elevated: #1a2332;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --text-dim: #475569;
        --border-color: rgba(255, 255, 255, 0.08);
        --border-hover: rgba(255, 255, 255, 0.15);
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4);
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.5);
        --shadow-glow: 0 0 40px var(--primary-glow);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;
        --radius-2xl: 24px;
        --transition-fast: 0.15s ease;
        --transition-normal: 0.25s ease;
        --transition-slow: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* ========== GLOBAL STYLES ========== */
    .stApp {
        background:
            radial-gradient(ellipse at 20% 0%, rgba(0, 180, 216, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 100%, rgba(124, 58, 237, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(0, 0, 0, 0.3) 0%, transparent 70%),
            linear-gradient(180deg, var(--bg-dark) 0%, var(--bg-darker) 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        min-height: 100vh;
    }

    /* Hide default Streamlit elements */
#MainMenu, footer { visibility: hidden; }  /* OK */
header {
    visibility: hidden !important;
    height: 0px !important;
}



    /* Removed top padding to move content to top */
    .main .block-container {
        padding: 0 3rem 4rem !important;
        padding-top: 0 !important;
        max-width: 1500px;
    }
    
    /* Remove ALL default Streamlit top spacing */
    .stApp > header {
        height: 0 !important;
        min-height: 0 !important;
    }
    
    .appview-container {
        padding-top: 0 !important;
    }
    
    section[data-testid="stAppViewContainer"] {
        padding-top: 0 !important;
    }
    
    .stAppViewBlockContainer {
        padding-top: 0 !important;
    }
    
    [data-testid="stAppViewContainer"] > section > div {
        padding-top: 0 !important;
    }
    
    .block-container {
        padding-top: 0 !important;
    }

    /* ========== TYPOGRAPHY ========== */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Poppins', sans-serif !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em;
    }

    p, span, div {
        color: var(--text-secondary);
    }

    /* Made title smaller and moved to top */
    .custom-header {
        text-align: center;
        font-size: clamp(18px, 2.5vw, 24px);
        font-weight: 700;
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 40%, var(--secondary-light) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 4px;
        padding-top: 5px;
        letter-spacing: -1px;
        filter: drop-shadow(0 0 40px var(--primary-glow));
        animation: headerPulse 4s ease-in-out infinite;
    }

    @keyframes headerPulse {
        0%, 100% { filter: drop-shadow(0 0 30px var(--primary-glow)); }
        50% { filter: drop-shadow(0 0 50px var(--secondary-glow)); }
    }

    /* Made subtitle smaller with minimal margins */
    .subtitle {
        text-align: center;
        font-size: 11px;
        color: var(--text-muted);
        margin-bottom: 8px;
        margin-top: 0;
        font-weight: 400;
        letter-spacing: 0.3px;
    }

    /* ========== DIVIDERS ========== */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, var(--primary) 20%, var(--secondary) 80%, transparent 100%);
        margin: 20px 0;
        opacity: 0.4;
    }

    /* ========== TAB STYLING ========== */
    .stTabs {
        background: transparent;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-card);
        border-radius: var(--radius-xl);
        padding: 10px;
        gap: 10px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-lg), inset 0 1px 0 rgba(255,255,255,0.05);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: var(--radius-md);
        color: #ffffff !important;
        font-weight: 600;
        font-size: 16px;
        padding: 14px 28px;
        transition: all var(--transition-normal);
        border: none;
        position: relative;
        overflow: hidden;
    }

    .stTabs [data-baseweb="tab"]::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        opacity: 0;
        transition: opacity var(--transition-normal);
        border-radius: var(--radius-md);
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--primary-light) !important;
    }

    .stTabs [data-baseweb="tab"]:hover::before {
        opacity: 0.1;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
        color: #0a0e17 !important;
        box-shadow: 0 4px 20px var(--primary-glow), inset 0 1px 0 rgba(255,255,255,0.2);
        font-weight: 700;
    }

    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    div[data-baseweb="tab"] button p,
    div[data-testid="stTabs"] button p {
        font-size: 17px !important;
        font-weight: 700 !important;
    }

    .stTabs [aria-selected="true"] p {
        color: #0a0e17 !important;
    }

    /* ========== BUTTON STYLING ========== */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: #0a0e17 !important;
        border: none;
        border-radius: var(--radius-md);
        padding: 14px 32px;
        font-weight: 700;
        font-size: 15px;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.3px;
        transition: all var(--transition-slow);
        box-shadow: 0 4px 20px var(--primary-glow), inset 0 1px 0 rgba(255,255,255,0.2);
        text-transform: uppercase;
        position: relative;
        overflow: hidden;
        text-shadow: none;
    }

    .stButton > button * {
        color: #0a0e17 !important;
    }

    .stButton > button p {
        color: #0a0e17 !important;
        font-weight: 700;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s ease;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px var(--primary-glow), inset 0 1px 0 rgba(255,255,255,0.3);
        color: #0a0e17 !important;
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    .stButton > button:active {
        transform: translateY(-1px);
        color: #0a0e17 !important;
    }

    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--secondary) 0%, #9333ea 100%);
        box-shadow: 0 4px 20px var(--secondary-glow);
        color: #ffffff !important;
        font-weight: 700;
    }

    .stDownloadButton > button * {
        color: #ffffff !important;
    }

    .stDownloadButton > button:hover {
        color: #ffffff !important;
    }

    /* ========== FILE UPLOADER ========== */
    .stFileUploader {
        background: var(--bg-card);
        border: 2px dashed var(--border-color);
        border-radius: var(--radius-xl);
        padding: 24px;
        transition: all var(--transition-normal);
    }

    .stFileUploader:hover {
        border-color: var(--primary);
        background: var(--info-bg);
        box-shadow: 0 0 30px var(--primary-glow);
    }

    .stFileUploader label {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }

    .stFileUploader [data-testid="stFileUploaderDropzone"] {
        background: transparent !important;
        border: none !important;
    }

    .stFileUploader small {
        color: var(--text-muted) !important;
    }

    /* ========== INPUT FIELDS ========== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
        padding: 14px 18px !important;
        font-size: 15px !important;
        font-family: 'Inter', sans-serif !important;
        transition: all var(--transition-normal) !important;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 4px var(--primary-glow) !important;
        outline: none !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: var(--text-dim) !important;
    }

    .stNumberInput [data-baseweb="input"] {
        background: var(--bg-card) !important;
        border-radius: var(--radius-md) !important;
    }

    /* ========== SELECTBOX ========== */
    .stSelectbox > div > div {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
    }

    .stSelectbox [data-baseweb="select"] > div {
        background: var(--bg-card) !important;
        border: none !important;
        color: var(--text-primary) !important;
    }

    /* ========== SLIDER ========== */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, var(--primary), var(--secondary)) !important;
        height: 6px !important;
        border-radius: 3px !important;
    }

    .stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] {
        background: var(--primary) !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: var(--radius-sm) !important;
        padding: 4px 8px !important;
    }

    .stSlider [data-testid="stTickBar"] > div {
        background: var(--border-color) !important;
    }

    /* ========== CHECKBOX ========== */
    .stCheckbox label {
        color: var(--text-secondary) !important;
        font-size: 14px !important;
    }

    .stCheckbox > div > div > div {
        background: var(--bg-card) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 6px !important;
    }

    /* ========== DATAFRAME/TABLE ========== */
    .stDataFrame {
        border-radius: var(--radius-lg) !important;
        overflow: hidden !important;
        border: 1px solid var(--border-color) !important;
        box-shadow: var(--shadow-md) !important;
    }

    .stDataFrame [data-testid="stDataFrameResizable"] {
        background: var(--bg-card) !important;
    }

    .stDataFrame th {
        background: var(--bg-elevated) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        padding: 12px 16px !important;
    }

    .stDataFrame td {
        color: var(--text-secondary) !important;
        padding: 10px 16px !important;
        border-bottom: 1px solid var(--border-color) !important;
    }

    /* ========== SIDEBAR ========== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f2e 0%, #0f0a1f 100%) !important;
        border-right: 2px solid var(--primary) !important;
        z-index: 999 !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, #1a1f2e 0%, #0f0a1f 100%) !important;
    }

    [data-testid="stSidebar"] .block-container {
        padding: 2rem 1.5rem;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-family: 'Poppins', sans-serif !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: #e0e0e0 !important;
    }

/* ==========================================================
   FIX SIDEBAR TOGGLE BUTTON (ICON VISIBLE + NOT OVERLAPPING)
   ========================================================== */

/* ==========================================================
   🔹 FINAL FULLY WORKING CSS FIX FOR SIDEBAR & TOGGLE
   🔹 DO NOT MODIFY ANYTHING INSIDE THIS BLOCK
   ========================================================== */

/* Restore the sidebar container */
[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    min-width: 300px !important;
    width: 320px !important;
    position: relative !important;
    overflow-x: visible !important;
    overflow-y: auto !important;
    transform: none !important;
    z-index: 1000 !important;
    background: linear-gradient(180deg, #1a1f2e 0%, #0f0a1f 100%) !important;
}

/* Restore and style the sidebar toggle icon */
[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    pointer-events: auto !important;
    opacity: 1 !important;
    visibility: visible !important;

    /* Let Streamlit handle positioning */
    position: relative !important;
    top: auto !important;
    left: auto !important;

    /* Icon appearance */
    width: 38px !important;
    height: 38px !important;
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid var(--primary) !important;
    border-radius: 10px !important;
    box-shadow: 0 0 6px var(--primary-glow) !important;
    cursor: pointer !important;
    transition: transform 0.2s ease-in-out;
    z-index: 2000 !important;
}

[data-testid="stSidebarCollapsedControl"]:hover {
    transform: scale(1.07);
    background: var(--primary) !important;
}

[data-testid="stSidebarCollapsedControl"] svg {
    color: var(--primary) !important;
}
[data-testid="stSidebarCollapsedControl"]:hover svg {
    color: #0a0e17 !important;
}

/* Ensure Streamlit doesn't hide our toggle */
[data-testid="collapsedControl"] {
    all: unset !important;
}

/* 🔸 Fix header/menu hiding without affecting sidebar or logo */
#MainMenu, footer {
    visibility: hidden !important;
}
header {
    visibility: hidden !important;
    height: 0 !important;
}

/* Prevent global CSS from collapsing width */
section[data-testid="stSidebar"] > div {
    width: auto !important;
}


/* ================== KEEP DEFAULT BUTTON LOGIC ================== */
[data-testid="collapsedControl"] {
    all: unset !important; /* Remove previous forced styling */
}


    [data-testid="stSidebar"] button[kind="header"],
    [data-testid="stSidebar"] [data-testid="stBaseButton-header"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        color: var(--primary) !important;
        background: rgba(0, 245, 255, 0.1) !important;
        border: 1px solid var(--primary) !important;
        border-radius: 8px !important;
        z-index: 9999 !important;
    }

    [data-testid="stSidebar"] button[kind="header"]:hover,
    [data-testid="stSidebar"] [data-testid="stBaseButton-header"]:hover {
        background: var(--primary) !important;
        color: #0a0e17 !important;
    }

    section[data-testid="stSidebar"] button {
        color: #ffffff !important;
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid var(--border-color) !important;
        pointer-events: auto !important;
    }

    section[data-testid="stSidebar"] button:hover {
        background: rgba(0, 245, 255, 0.1) !important;
        border-color: var(--primary) !important;
    }

    /* ========== GLASS CARD ========== */
    .glass-card {
        background: rgba(17, 24, 39, 0.7);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-xl);
        padding: 28px;
        box-shadow: var(--shadow-lg), inset 0 1px 0 rgba(255,255,255,0.05);
        transition: all var(--transition-slow);
        position: relative;
        overflow: hidden;
    }

    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    }

    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-glow), var(--shadow-lg);
        border-color: var(--primary);
    }

    /* ========== STAT CARDS ========== */
    .stat-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 24px;
        text-align: center;
        transition: all var(--transition-slow);
        position: relative;
        overflow: hidden;
    }

    .stat-card::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        transform: scaleX(0);
        transition: transform var(--transition-slow);
    }

    .stat-card:hover {
        border-color: var(--primary);
        box-shadow: 0 8px 30px var(--primary-glow);
        transform: translateY(-2px);
    }

    .stat-card:hover::after {
        transform: scaleX(1);
    }

    .stat-value {
        font-size: 36px;
        font-weight: 800;
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
    }

    .stat-label {
        color: var(--text-muted);
        font-size: 14px;
        font-weight: 500;
        margin-top: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ========== SECTION HEADERS ========== */
    .section-header {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 24px;
        padding-bottom: 16px;
        border-bottom: 1px solid var(--border-color);
    }

    .section-header h3 {
        margin: 0 !important;
        color: var(--text-primary) !important;
        font-size: 20px !important;
        font-weight: 700 !important;
    }

    .section-icon {
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        box-shadow: 0 4px 15px var(--primary-glow);
    }

    /* ========== CHAT STYLING ========== */
    .chat-container {
        background: var(--bg-card);
        border-radius: var(--radius-xl);
        padding: 20px;
        border: 1px solid var(--border-color);
        max-height: 350px;
        overflow-y: auto;
        margin-bottom: 16px;
    }

    .chat-message-user {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        padding: 14px 20px;
        border-radius: 20px 20px 6px 20px;
        margin: 10px 0;
        margin-left: 25%;
        font-size: 14px;
        box-shadow: 0 4px 15px var(--primary-glow);
        animation: slideInRight 0.3s ease-out;
        line-height: 1.5;
    }

    .chat-message-bot {
        background: var(--bg-elevated);
        color: var(--text-primary);
        padding: 14px 20px;
        border-radius: 20px 20px 20px 6px;
        margin: 10px 0;
        margin-right: 25%;
        font-size: 14px;
        border: 1px solid var(--border-color);
        animation: slideInLeft 0.3s ease-out;
        line-height: 1.5;
    }

    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }

    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }

    /* ========== ALERT MESSAGES ========== */
    .stSuccess {
        background: var(--success-bg) !important;
        border: 1px solid var(--success) !important;
        border-radius: var(--radius-md) !important;
        color: var(--success) !important;
        padding: 14px 18px !important;
    }

    .stInfo {
        background: var(--info-bg) !important;
        border: 1px solid var(--primary) !important;
        border-radius: var(--radius-md) !important;
        color: var(--primary-light) !important;
        padding: 14px 18px !important;
    }

    .stWarning {
        background: var(--warning-bg) !important;
        border: 1px solid var(--warning) !important;
        border-radius: var(--radius-md) !important;
        padding: 14px 18px !important;
    }

    .stError {
        background: var(--error-bg) !important;
        border: 1px solid var(--error) !important;
        border-radius: var(--radius-md) !important;
        padding: 14px 18px !important;
    }

    /* ========== PROGRESS BAR ========== */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--primary), var(--secondary)) !important;
        border-radius: 4px !important;
    }

    .stProgress > div > div {
        background: var(--bg-card) !important;
        border-radius: 4px !important;
    }

    /* ========== SPINNER ========== */
    .stSpinner > div {
        border-top-color: var(--primary) !important;
    }

    /* ========== IMAGE CONTAINER ========== */
    .stImage {
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--border-color);
    }

    /* ========== METRICS ========== */
    [data-testid="stMetricValue"] {
        color: var(--primary) !important;
        font-weight: 700 !important;
        font-size: 28px !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
    }

    /* ========== EXPANDER ========== */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        border: 1px solid var(--border-color) !important;
    }

    .streamlit-expanderContent {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
    }

    /* ========== CUSTOM SCROLLBAR ========== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-dark);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--primary), var(--secondary));
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-light);
    }

    /* ========== COLUMN SPACING ========== */
    [data-testid="column"] {
        padding: 0 10px;
    }

    /* ========== LABELS ========== */
    .stSelectbox label,
    .stTextInput label,
    .stNumberInput label,
    .stSlider label,
    .stFileUploader label {
        color: var(--text-primary) !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        margin-bottom: 8px !important;
    }

    /* ========== CAPTIONS ========== */
    .stCaption {
        color: var(--text-muted) !important;
        font-size: 13px !important;
    }

    /* ========== PROJECT LIST ITEM ========== */
    .project-item {
        padding: 10px 14px;
        background: rgba(0, 180, 216, 0.08);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-sm);
        margin: 6px 0;
        font-size: 13px;
        color: var(--text-secondary);
        transition: all var(--transition-fast);
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .project-item:hover {
        background: rgba(0, 180, 216, 0.15);
        border-color: var(--primary);
        color: var(--text-primary);
    }

    /* ========== TOOLTIP ========== */
    [data-testid="stTooltipIcon"] {
        color: var(--text-muted) !important;
    }

    /* ========== ANIMATIONS ========== */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .fade-in {
        animation: fadeIn 0.4s ease-out;
    }

    /* ========== RESPONSIVE ========== */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0 1.5rem 4rem !important;
        }

        .custom-header {
            font-size: 20px;
        }

        .subtitle {
            font-size: 10px;
        }

        .stat-value {
            font-size: 28px;
        }
    }
        .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 40px var(--shadow-glow);
        border-color: var(--primary-light);
    }
/* ========== GLASS CARD ========== */
.glass-card {
    background: rgba(17, 24, 39, 0.7);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-xl);
    padding: 28px;
    box-shadow: var(--shadow-lg), inset 0 1px 0 rgba(255,255,255,0.05);
    transition: all var(--transition-slow);
    position: relative;
    overflow: hidden;
}

.glass-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
}

.glass-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 40px var(--primary-glow), inset 0 1px 0 rgba(255,255,255,0.2);
    border-color: var(--primary-light);
}

</style>
""", unsafe_allow_html=True)


# =================================================================================
# LOGO FUNCTION - Logo is no longer fixed, flows with content
# =================================================================================
def load_logo_top_right():
    logo_path = os.path.join(os.getcwd(), "logo.png")
    if not os.path.exists(logo_path):
        return

    encoded_logo = base64.b64encode(open(logo_path, "rb").read()).decode()

    st.markdown(f"""
    <style>
    .header-container {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 5px 20px 0 20px;
        margin: 0;
        margin-top: 5px;
        padding-top: 5px;
    }}
    
    .logo-container {{
        width: 70px;
        height: auto;
        filter: drop-shadow(0 4px 16px rgba(0, 180, 216, 0.3));
        transition: all 0.3s ease;
    }}

    .logo-container:hover {{
        transform: scale(1.05);
        filter: drop-shadow(0 6px 24px rgba(0, 180, 216, 0.5));
    }}
    </style>

    <div class="header-container">
        <img src="data:image/png;base64,{encoded_logo}" class="logo-container">
    </div>
    """, unsafe_allow_html=True)

# Call the function
load_logo_top_right()

# Header with subtitle - reduced margins
st.markdown("""
    <div class="custom-header">EV Analysis Tool</div>
    <p class="subtitle">Advanced Extracellular Vesicle Analysis & Particle Size Estimation</p>
""", unsafe_allow_html=True)

st.markdown("---")

# -------------------------
# Helper functions
# -------------------------
def save_uploadedfile_to_path(uploaded_file, dest_folder="uploads"):
    """Save a Streamlit UploadedFile to disk and return its path."""
    if isinstance(uploaded_file, str) and os.path.exists(uploaded_file):
        return uploaded_file
    dest_path = os.path.join(dest_folder, uploaded_file.name)  # type: ignore[attr-defined]
    base, ext = os.path.splitext(dest_path)
    i = 1
    while os.path.exists(dest_path):
        dest_path = f"{base}_{i}{ext}"
        i += 1
    with open(dest_path, "wb") as f:
        f.write(uploaded_file.getbuffer())  # type: ignore[attr-defined]
    return dest_path

def convert_anyfile_to_parquet(uploaded_file_or_path):
    """Convert uploaded file to parquet. Supports .fcs, .csv, .xlsx/.xls, .json."""
    if isinstance(uploaded_file_or_path, str) and os.path.exists(uploaded_file_or_path):
        path = uploaded_file_or_path
    else:
        path = save_uploadedfile_to_path(uploaded_file_or_path, dest_folder="uploads")

    lower = path.lower()
    try:
        if lower.endswith(".fcs"):
            if not use_fcsparser:
                st.error("fcsparser not installed. Install with: pip install fcsparser")
                return None, None
            meta, df = fcsparser.parse(path, reformat_meta=True)  # type: ignore[misc]
        elif lower.endswith(".csv"):
            df = pd.read_csv(path)
        elif lower.endswith(".parquet"):
            df = pd.read_parquet(path)
            return path, df
        elif lower.endswith((".xlsx", ".xls")):
            df = pd.read_excel(path)
        elif lower.endswith(".json"):
            df = pd.read_json(path)
        else:
            st.error("Unsupported file type for conversion.")
            return None, None

        if use_pyarrow:
            parquet_path = os.path.join("uploads", os.path.basename(path).rsplit(".", 1)[0] + ".parquet")
            try:
                table = pa.Table.from_pandas(df)
                pq.write_table(table, parquet_path)
                return parquet_path, df
            except Exception as e:
                st.warning(f"Parquet conversion failed: {e}. Returning dataframe without parquet.")
                return None, df
        else:
            csv_path = os.path.join("uploads", os.path.basename(path).rsplit(".", 1)[0] + ".csv")
            df.to_csv(csv_path, index=False)
            return csv_path, df
    except Exception as e:
        st.error(f"Failed to convert file: {e}")
        return None, None

def load_dataframe_from_uploaded(uploaded_file_or_path):
    """Load dataframe and return (df, source_path)."""
    parquet_path, df = convert_anyfile_to_parquet(uploaded_file_or_path)
    if parquet_path and os.path.exists(parquet_path) and parquet_path.lower().endswith(".parquet"):
        try:
            df2 = pd.read_parquet(parquet_path)
            return df2, parquet_path
        except Exception:
            return df, parquet_path
    return df, parquet_path

# -------------------------
# Theoretical lookup (Mie or fallback)
# -------------------------
@st.cache_data(show_spinner=False)
def build_theoretical_lookup(lambda_nm, n_particle, n_medium, fsc_range, ssc_range, diameters):  # type: ignore[no-untyped-def]
    angles = np.linspace(0, 180, 1000)
    ratios = np.zeros_like(diameters, dtype=float)
    if use_pymiescatt:
        for i, D in enumerate(diameters):
            try:
                intensity = PMS.ScatteringFunction(n_particle / n_medium, D, lambda_nm, angles, nMedium=n_medium)[0]
                mask_f = (angles >= fsc_range[0]) & (angles <= fsc_range[1])
                mask_s = (angles >= ssc_range[0]) & (angles <= ssc_range[1])
                I_FSC = np.trapz(intensity[mask_f], angles[mask_f])  # type: ignore[arg-type]
                I_SSC = np.trapz(intensity[mask_s], angles[mask_s])  # type: ignore[arg-type]
                ratios[i] = float(I_FSC) / float(I_SSC) if I_SSC != 0 else np.nan
            except Exception:
                ratios[i] = np.nan
        if not np.any(np.isfinite(ratios)):
            ratios = np.zeros_like(diameters, dtype=float)
        else:
            ratios = np.nan_to_num(ratios, nan=np.nanmax(ratios[np.isfinite(ratios)]))
    else:
        A = 1e-6; p = 5.5; B = 1e-2; q = 3.0
        ratios = (A * diameters**p) / (B + diameters**q)
        ratios = np.maximum.accumulate(ratios)
    return angles, ratios

def estimate_diameters_vectorized(measured_ratios, theoretical_ratios, diameters):
    """
    Vectorized particle size estimation - much faster than row-by-row iteration.
    Uses NumPy broadcasting to find the closest theoretical ratio for each measured ratio.
    """
    # Convert to numpy arrays
    measured = np.asarray(measured_ratios)
    theoretical = np.asarray(theoretical_ratios)
    diams = np.asarray(diameters)
    
    # Create output arrays
    n = len(measured)
    estimated_diameters = np.full(n, np.nan)
    matched_ratios = np.full(n, np.nan)
    matched_indices = np.full(n, np.nan)
    
    # Find valid (non-NaN) measurements
    valid_mask = np.isfinite(measured)
    valid_measured = measured[valid_mask]
    
    if len(valid_measured) > 0:
        # Broadcasting: compute absolute differences for all valid measurements at once
        # Shape: (n_valid, n_theoretical)
        diffs = np.abs(valid_measured[:, np.newaxis] - theoretical[np.newaxis, :])
        
        # Find best match index for each measurement
        best_indices = np.argmin(diffs, axis=1)
        
        # Assign results
        estimated_diameters[valid_mask] = diams[best_indices]
        matched_ratios[valid_mask] = theoretical[best_indices]
        matched_indices[valid_mask] = best_indices
    
    return estimated_diameters, matched_ratios, matched_indices


# -------------------------
# Chatbot (simple)
# -------------------------
def analyze_file_for_chat(path_or_uploaded):
    df, src = load_dataframe_from_uploaded(path_or_uploaded)
    if df is None:
        return "Cannot load file."
    try:
        return "Quick Dataset Summary:<br>" + df.describe(include="all").to_html(classes="table table-striped", border=0)
    except Exception as e:
        return f"Error summarizing file: {e}"

def chatbot_ui(uploaded):
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.markdown('<div class="section-header"><div class="section-icon">💬</div><h3>Analysis Chatbot</h3></div>', unsafe_allow_html=True)

    # Chat messages container
    chat_html = '<div class="chat-container">'
    for sender, text in st.session_state.chat_history:
        if sender == "You":
            chat_html += f'<div class="chat-message-user"><b>{sender}:</b> {text}</div>'
        else:
            chat_html += f'<div class="chat-message-bot"><b>{sender}:</b> {text}</div>'
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    user_input = st.text_input("Type your message:", key="chat_input", placeholder="Ask about your data...")
    if st.button("Send Message", key="send_btn"):
        if user_input.strip():
            st.session_state.chat_history.append(("You", user_input))
            m = user_input.lower()
            if "hello" in m or "hi" in m:
                reply = "Hello! How can I assist with your EV analysis today?"
            elif "analy" in m:
                reply = analyze_file_for_chat(uploaded) if uploaded else "Please upload a file first."
            else:
                reply = "Try asking about pH, temperature, anomalies, 'analyze data', or 'size'."
            st.session_state.chat_history.append(("Bot", reply))
            st.rerun()


# -------------------------
# API Connection Check
# -------------------------
if "api_connection_checked" not in st.session_state:
    st.session_state.api_connection_checked = False
    st.session_state.api_available = False

if not st.session_state.api_connection_checked:
    with st.spinner("🔌 Connecting to backend API..."):
        st.session_state.api_available = check_api_connection()
        st.session_state.api_connection_checked = True
        
if st.session_state.api_available:
    st.success("✅ Connected to backend API at http://localhost:8000", icon="✅")
else:
    st.error("⚠️ Backend API not available. Please start the FastAPI server: `uvicorn src.api.main:app --reload`", icon="⚠️")

# -------------------------
# Tabs
# -------------------------
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🧪 Flow Cytometry", "⚛ Nanoparticle Tracking"])


# -------------------------
# TAB 1: Dashboard + Upload + Chatbot
# -------------------------
with tab1:
    with st.sidebar:
        st.markdown('<div class="section-header"><div class="section-icon">🧪</div><h3>Sample Database</h3></div>', unsafe_allow_html=True)
        
        # Sample list from API
        if st.session_state.get("api_available", False):
            try:
                client = get_client()
                
                # Filters
                st.markdown("**Filters**")
                filter_treatment = st.selectbox(
                    "Treatment",
                    options=["All", "CD81", "CD9", "CD63", "Isotype Control", "Other"],
                    key="filter_treatment"
                )
                
                filter_status = st.selectbox(
                    "Status",
                    options=["All", "uploaded", "processing", "completed", "failed"],
                    key="filter_status"
                )
                
                # Fetch samples
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button("🔄 Refresh", key="refresh_samples", use_container_width=True):
                        st.session_state.samples_last_refresh = time.time()
                with col2:
                    st.caption(f"")
                
                # Get samples with filters
                treatment_filter = None if filter_treatment == "All" else filter_treatment
                status_filter = None if filter_status == "All" else filter_status
                
                samples_response = client.get_samples(
                    skip=0,
                    limit=20,
                    treatment=treatment_filter,
                    status=status_filter
                )
                
                if samples_response and samples_response.get('samples'):
                    samples = samples_response['samples']
                    st.caption(f"Showing {len(samples)} of {samples_response.get('total', len(samples))} samples")
                    
                    # Display samples as cards
                    for sample in samples:
                        with st.expander(f"📋 {sample.get('sample_id', 'Unknown')}", expanded=False):
                            st.markdown(f"**Treatment:** {sample.get('treatment', 'N/A')}")
                            st.markdown(f"**Status:** {sample.get('status', 'N/A')}")
                            st.markdown(f"**Created:** {sample.get('created_at', 'N/A')[:10] if sample.get('created_at') else 'N/A'}")
                            if st.button(f"View Details", key=f"view_{sample.get('id')}"):
                                st.session_state.selected_sample_id = sample.get('id')
                                st.rerun()
                else:
                    st.info("No samples found. Upload a file to get started.")
            
            except Exception as e:
                st.error(f"Error loading samples: {str(e)}")
                st.caption("Check if backend API is running")
        else:
            # Fallback to file list if API not available
            st.markdown('<div class="section-header"><div class="section-icon">📁</div><h3>Previous Projects</h3></div>', unsafe_allow_html=True)
            imgs = [f for f in os.listdir("images") if f.endswith(".png") or f.endswith(".parquet")]
            if imgs:
                for im in imgs:
                    st.markdown(f'<div class="project-item">📄 {im}</div>', unsafe_allow_html=True)
            else:
                st.info("No previous projects yet.")
        
        st.markdown("---")
        st.caption("Expand this sidebar from the top-left arrow.")

    st.markdown('<div class="section-header"><div class="section-icon">📈</div><h3>Generated Graphs & Chat</h3></div>', unsafe_allow_html=True)
    left_col, right_col = st.columns([3, 1])

    with left_col:
        graph_files = [f for f in os.listdir("images") if f.endswith(".png")]
        if graph_files:
            for gf in graph_files[:2]:
                st.image(os.path.join("images", gf), caption=gf, use_container_width=True)
        else:
            st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 60px 40px;">
                <div style="font-size: 56px; margin-bottom: 20px;">📊</div>
                <h3 style="color: #f8fafc; margin-bottom: 12px;">No Graphs Generated Yet</h3>
                <p style="color: #94a3b8; margin: 0;">Upload a dataset and run analysis to generate visualizations</p>
            </div>
            """, unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="section-header"><div class="section-icon">📥</div><h3>Upload File</h3></div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload project/dataset",
            type=["csv", "xlsx", "json", "fcs", "parquet"],
            help="Supported formats: CSV, Excel, JSON, FCS, Parquet"
        )

        # Metadata Form - Capture sample information
        if uploaded_file:
            # Check if this is a new file upload - reset metadata form if so
            if (
                "last_uploaded_file" not in st.session_state
                or st.session_state.last_uploaded_file != uploaded_file.name
            ):
                st.session_state.last_uploaded_file = uploaded_file.name
                st.session_state.metadata_submitted = False
                st.session_state.chat_history = []
                # Clear previous metadata
                for key in ["sample_id", "treatment", "concentration_ug", "preparation_method", "operator", "notes"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.info("🆕 New dataset detected. Please fill in the metadata form below.")
            
            st.markdown('<div class="section-header" style="margin-top: 20px;"><div class="section-icon">📋</div><h4>Sample Metadata</h4></div>', unsafe_allow_html=True)
            
            with st.form("metadata_form", clear_on_submit=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    sample_id = st.text_input(
                        "Sample ID *",
                        value=st.session_state.get("sample_id", ""),
                        help="Unique identifier for this sample",
                        placeholder="e.g., L5_F10_CD81"
                    )
                    
                    treatment = st.text_input(
                        "Treatment",
                        value=st.session_state.get("treatment", ""),
                        help="Treatment or antibody used",
                        placeholder="e.g., CD81, CD9, Isotype Control"
                    )
                    
                    concentration_ug = st.number_input(
                        "Concentration (μg)",
                        min_value=0.0,
                        max_value=100.0,
                        value=st.session_state.get("concentration_ug", 0.0),
                        step=0.1,
                        help="Antibody or treatment concentration in micrograms"
                    )
                
                with col2:
                    preparation_method = st.selectbox(
                        "Preparation Method",
                        options=["", "SEC", "Centrifugation", "Ultracentrifugation", "Other"],
                        index=0,
                        help="EV isolation method"
                    )
                    
                    operator = st.text_input(
                        "Operator",
                        value=st.session_state.get("operator", ""),
                        help="Person who performed the experiment",
                        placeholder="Enter your name"
                    )
                
                notes = st.text_area(
                    "Notes",
                    value=st.session_state.get("notes", ""),
                    help="Additional observations or comments",
                    placeholder="Enter any relevant notes about this sample...",
                    height=80
                )
                
                submit_metadata = st.form_submit_button("✅ Save Metadata & Process File", use_container_width=True)
                
                if submit_metadata:
                    # Validation
                    errors = []
                    if not sample_id or not sample_id.strip():  # type: ignore[union-attr]
                        errors.append("❌ Sample ID is required")
                    if concentration_ug < 0:
                        errors.append("❌ Concentration cannot be negative")
                    
                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        # Store in session state
                        st.session_state.sample_id = sample_id
                        st.session_state.treatment = treatment
                        st.session_state.concentration_ug = concentration_ug
                        st.session_state.preparation_method = preparation_method
                        st.session_state.operator = operator
                        st.session_state.notes = notes
                        st.session_state.metadata_submitted = True
                        st.success("✅ Metadata saved successfully!")
        
        if uploaded_file and st.session_state.get("metadata_submitted", False):
            # Process file via API
            if st.session_state.api_available:
                with st.spinner("📤 Uploading file to backend API..."):
                    try:
                        # Save uploaded file temporarily
                        temp_path = save_uploadedfile_to_path(uploaded_file, dest_folder="uploads")
                        
                        # Determine file type and upload via API
                        file_ext = uploaded_file.name.split('.')[-1].lower()  # type: ignore[union-attr]
                        
                        client = get_client()
                        
                        if file_ext == 'fcs':
                            # Upload FCS file with metadata
                            response = client.upload_fcs(
                                file_path=temp_path,
                                sample_id=st.session_state.sample_id,
                                treatment=st.session_state.treatment or "",
                                concentration_ug=st.session_state.concentration_ug,
                                preparation_method=st.session_state.preparation_method or "",
                                operator=st.session_state.operator or "",
                                notes=st.session_state.notes or ""
                            )
                        elif file_ext == 'nta' or 'nta' in str(uploaded_file.name).lower():  # type: ignore[union-attr]
                            # Upload NTA file with metadata
                            response = client.upload_nta(
                                file_path=temp_path,
                                sample_id=st.session_state.sample_id,
                                treatment=st.session_state.treatment or "",
                                concentration_ug=st.session_state.concentration_ug,
                                preparation_method=st.session_state.preparation_method or "",
                                operator=st.session_state.operator or "",
                                notes=st.session_state.notes or ""
                            )
                        else:
                            st.warning(f"⚠️ Unsupported file type for API upload: {file_ext}. Processing locally instead.")
                            # Fallback to local processing
                            parquet_path, df_loaded = convert_anyfile_to_parquet(uploaded_file)
                            if df_loaded is not None:
                                st.dataframe(df_loaded.head(), width='stretch')  # type: ignore[union-attr]
                            chatbot_ui(parquet_path if parquet_path else uploaded_file)
                            response = None
                        
                        if response:
                            # Get database ID (numeric primary key) for API calls
                            uploaded_db_id = response.get('id')
                            uploaded_sample_id = response.get('sample_id')
                            
                            # If no database ID returned, use sample_id as fallback
                            if uploaded_db_id is None:
                                st.warning(f"⚠️ No database ID returned, using sample_id as fallback")
                                uploaded_db_id = uploaded_sample_id
                            
                            st.success(f"✅ File uploaded successfully! Sample ID: {uploaded_sample_id}")
                            
                            # Display sample metadata directly from upload response
                            st.markdown("**📋 Sample Information:**")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Sample ID", response.get('sample_id', 'N/A'))
                                st.metric("Treatment", response.get('treatment', 'N/A') or 'N/A')
                            with col2:
                                st.metric("Concentration (μg)", response.get('concentration_ug', 'N/A') or 'N/A')
                                st.metric("Preparation", response.get('preparation_method', 'N/A') or 'N/A')
                            with col3:
                                st.metric("Operator", response.get('operator', 'N/A') or 'N/A')
                                st.metric("Status", response.get('status', 'N/A'))
                            
                            if response.get('notes'):
                                st.info(f"📝 Notes: {response['notes']}")
                            
                            # Display parsed FCS results if available
                            if response.get('fcs_results'):
                                fcs_data = response['fcs_results']
                                st.markdown("**🔬 FCS Analysis Results (Parsed by Professional Parser):**")
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("Total Events", f"{fcs_data.get('event_count', 0):,}")
                                    if fcs_data.get('mean_fsc'):
                                        st.metric("Mean FSC", f"{fcs_data['mean_fsc']:.1f}")
                                with col2:
                                    st.metric("Channels", len(fcs_data.get('channels', [])))
                                    if fcs_data.get('mean_ssc'):
                                        st.metric("Mean SSC", f"{fcs_data['mean_ssc']:.1f}")
                                
                                # Show available channels
                                if fcs_data.get('channels'):
                                    with st.expander("📊 Available Channels"):
                                        st.write(", ".join(fcs_data['channels'][:15]))
                                        if len(fcs_data['channels']) > 15:
                                            st.caption(f"... and {len(fcs_data['channels']) - 15} more channels")
                            else:
                                st.info("ℹ️ File uploaded. Parsing in progress...")
                            
                            # Show upload confirmation
                            st.info(f"ℹ️ Processing job ID: {response.get('job_id', 'N/A')}")
                            st.info(f"ℹ️ File size: {response.get('file_size_mb', 0):.2f} MB")
                            
                            # Store database ID for chatbot context
                            st.session_state.current_sample_id = uploaded_db_id
                            st.session_state.current_sample_name = uploaded_sample_id
                            chatbot_ui(uploaded_db_id)
                    
                    except Exception as e:
                        st.error(f"❌ Error uploading file: {str(e)}")
                        st.info("ℹ️ Falling back to local processing...")
                        # Fallback to local processing
                        parquet_path, df_loaded = convert_anyfile_to_parquet(uploaded_file)
                        if df_loaded is not None:
                            st.dataframe(df_loaded.head(), width='stretch')  # type: ignore[union-attr]
                        chatbot_ui(parquet_path if parquet_path else uploaded_file)
            else:
                # API not available - use local processing
                st.warning("⚠️ Backend API not available. Processing file locally...")
                parquet_path, df_loaded = convert_anyfile_to_parquet(uploaded_file)

                if parquet_path is None and df_loaded is None:
                    st.error("Failed to convert uploaded file.")
                else:
                    try:
                        target = os.path.join("images", os.path.basename(parquet_path)) if parquet_path else None
                        if parquet_path and os.path.exists(parquet_path):
                            os.replace(parquet_path, target)
                            saved_path = target
                        else:
                            if df_loaded is not None and use_pyarrow:
                                target = os.path.join(
                                    "images",
                                    os.path.basename(str(uploaded_file.name).rsplit('.', 1)[0]) + ".parquet"  # type: ignore[union-attr]
                                )
                                pq.write_table(pa.Table.from_pandas(df_loaded), target)  # type: ignore[name-defined]
                                saved_path = target
                            else:
                                target = os.path.join(
                                    "images",
                                    os.path.basename(str(uploaded_file.name).rsplit('.', 1)[0]) + ".csv"  # type: ignore[union-attr]
                                )
                                if df_loaded is not None:
                                    df_loaded.to_csv(target, index=False)  # type: ignore[union-attr]
                                saved_path = target
                    except Exception:
                        saved_path = None

                    st.markdown("**Data Preview:**")
                    if df_loaded is not None:
                        st.dataframe(df_loaded.head(), width='stretch')  # type: ignore[union-attr]

                    if saved_path:
                        st.success(f"Saved: {os.path.basename(saved_path)}")

                    chatbot_ui(saved_path if saved_path else uploaded_file)
        
        elif uploaded_file and not st.session_state.get("metadata_submitted", False):
            st.info("👆 Please fill in the sample metadata form above and click 'Save Metadata & Process File' to continue.")

        else:
            st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 40px;">
                <div style="font-size: 42px; margin-bottom: 16px;">📤</div>
                <p style="color: #94a3b8; margin: 0;">Drag & drop or click to upload</p>
            </div>
            """, unsafe_allow_html=True)
            chatbot_ui(None)

# -------------------------
# TAB 2: Particle Size Analysis
# -------------------------
with tab2:
    with st.sidebar:
        st.markdown('<div class="section-header"><div class="section-icon">⚙️</div><h3>Analysis Settings</h3></div>', unsafe_allow_html=True)
        lambda_nm = st.number_input("Laser wavelength (nm)", value=488.0, step=1.0)
        n_particle = st.number_input("Particle refractive index", value=1.38, step=0.01)
        n_medium = st.number_input("Medium refractive index", value=1.33, step=0.01)
        fsc_range = st.slider("FSC angle range (deg)", 0, 30, (1, 15), step=1)
        ssc_range = st.slider("SSC angle range (deg)", 30, 180, (85, 95), step=1)
        d_min, d_max = st.slider("Diameter search range (nm)", 10, 500, (40, 180), step=1)
        n_points = st.number_input("Diameter points (resolution)", value=200, min_value=20, max_value=2000, step=10)
        st.markdown("---")
        
        # =====================================================================
        # USER-DEFINED SIZE RANGES (Nov 27, 2025 - Jaganmohan requirement)
        # Let users choose their own size categories dynamically
        # =====================================================================
        st.markdown('<div class="section-header"><div class="section-icon">📊</div><h4>Size Range Analysis</h4></div>', unsafe_allow_html=True)
        st.caption("Define custom size ranges to count particles. Different scientific applications need different segmentation.")
        
        # Initialize session state for size ranges
        if "custom_size_ranges" not in st.session_state:
            # Default ranges based on common EV categorizations
            st.session_state.custom_size_ranges = [
                {"name": "Small EVs", "min": 30, "max": 100},
                {"name": "Medium EVs", "min": 100, "max": 150},
                {"name": "Large EVs", "min": 150, "max": 200},
            ]
        
        # Show current ranges
        st.markdown("**Current Size Ranges:**")
        ranges_to_remove = []
        for i, r in enumerate(st.session_state.custom_size_ranges):
            col_name, col_range, col_del = st.columns([2, 2, 1])
            with col_name:
                st.text(f"{r['name']}")
            with col_range:
                st.text(f"{r['min']}-{r['max']} nm")
            with col_del:
                if st.button("🗑️", key=f"del_range_{i}", help="Remove this range"):
                    ranges_to_remove.append(i)
        
        # Remove marked ranges
        for idx in sorted(ranges_to_remove, reverse=True):
            st.session_state.custom_size_ranges.pop(idx)
            st.rerun()
        
        # Add new range section
        with st.expander("➕ Add New Size Range", expanded=False):
            new_range_name = st.text_input("Range Name", value="", placeholder="e.g., Small vesicles", key="new_range_name")
            new_range_cols = st.columns(2)
            with new_range_cols[0]:
                new_range_min = st.number_input("Min Size (nm)", min_value=0, max_value=500, value=30, step=5, key="new_range_min")
            with new_range_cols[1]:
                new_range_max = st.number_input("Max Size (nm)", min_value=0, max_value=500, value=100, step=5, key="new_range_max")
            
            if st.button("Add Range", key="add_size_range", use_container_width=True):
                if new_range_name.strip() and new_range_min < new_range_max:
                    st.session_state.custom_size_ranges.append({
                        "name": new_range_name.strip(),
                        "min": int(new_range_min),
                        "max": int(new_range_max)
                    })
                    st.success(f"Added: {new_range_name} ({new_range_min}-{new_range_max} nm)")
                    st.rerun()
                elif new_range_min >= new_range_max:
                    st.error("Min size must be less than max size")
                else:
                    st.error("Please enter a range name")
        
        # Quick preset buttons
        st.markdown("**Quick Presets:**")
        preset_cols = st.columns(2)
        with preset_cols[0]:
            if st.button("30-100, 100-150", key="preset_1", use_container_width=True, help="Standard EV categorization"):
                st.session_state.custom_size_ranges = [
                    {"name": "Small EVs (30-100)", "min": 30, "max": 100},
                    {"name": "Medium EVs (100-150)", "min": 100, "max": 150},
                ]
                st.rerun()
        with preset_cols[1]:
            if st.button("40-80, 80-120", key="preset_2", use_container_width=True, help="Exosome-focused ranges"):
                st.session_state.custom_size_ranges = [
                    {"name": "Exosomes (40-80)", "min": 40, "max": 80},
                    {"name": "Small MVs (80-120)", "min": 80, "max": 120},
                ]
                st.rerun()
        
        st.markdown("---")
        st.markdown("**Channels & Cleaning**")
        st.caption("Select columns after uploading the file.")
        ignore_negative = st.checkbox("Ignore negative -H values (replace with NaN)", value=True)
        drop_na = st.checkbox("Drop rows missing FSC/SSC after cleaning", value=True)
        st.markdown("---")
        if use_pymiescatt:
            st.success("PyMieScatt detected - full Mie used")
        else:
            st.warning("PyMieScatt not found - running fallback (approximate)")

    st.markdown('<div class="section-header"><div class="section-icon">🔬</div><h3>Particle Size vs Scatter Intensity Analysis</h3></div>', unsafe_allow_html=True)
    st.markdown("Upload FCS/Parquet/CSV/XLSX file with height channels (VFSC-H, VSSC1-H, etc.) to analyze particle size distribution using Mie scattering theory.")

    file2 = st.file_uploader("Upload dataset for analysis", type=["csv", "xlsx", "json", "fcs", "parquet"], key="analysis_upload")

    if "fsc_col_selected" not in st.session_state:
        st.session_state["fsc_col_selected"] = None
    if "ssc_col_selected" not in st.session_state:
        st.session_state["ssc_col_selected"] = None
    if "analysis_df" not in st.session_state:
        st.session_state["analysis_df"] = None

    if file2:
        # Option to upload via API
        if st.session_state.get("api_available", False):
            with st.expander("📋 Sample Metadata (Optional - for API upload)", expanded=False):
                st.caption("Fill this form to upload file to backend API and track in database")
                
                col1, col2 = st.columns(2)
                with col1:
                    tab2_sample_id = st.text_input(
                        "Sample ID",
                        value=st.session_state.get("tab2_sample_id", ""),
                        key="tab2_sample_id_input",
                        placeholder="e.g., L5_F10_CD81"
                    )
                    tab2_treatment = st.text_input(
                        "Treatment",
                        value=st.session_state.get("tab2_treatment", ""),
                        key="tab2_treatment_input",
                        placeholder="e.g., CD81, CD9"
                    )
                with col2:
                    tab2_concentration = st.number_input(
                        "Concentration (μg)",
                        min_value=0.0,
                        value=st.session_state.get("tab2_concentration", 0.0),
                        key="tab2_concentration_input"
                    )
                    tab2_method = st.selectbox(
                        "Preparation Method",
                        options=["", "SEC", "Centrifugation", "Ultracentrifugation"],
                        key="tab2_method_input"
                    )
                
                if st.button("📤 Upload to API & Analyze", key="tab2_api_upload"):
                    if tab2_sample_id and tab2_sample_id.strip():
                        try:
                            client = get_client()
                            
                            # Save file temporarily
                            temp_path = save_uploadedfile_to_path(file2, dest_folder="uploads")
                            
                            # Upload to API
                            with st.spinner("📤 Uploading to backend..."):
                                file_ext = str(file2.name).lower().split('.')[-1]  # type: ignore[union-attr]
                                
                                if file_ext == 'fcs':
                                    response = client.upload_fcs(
                                        file_path=temp_path,
                                        sample_id=tab2_sample_id,
                                        treatment=tab2_treatment,
                                        concentration_ug=tab2_concentration,
                                        preparation_method=tab2_method,
                                        operator=st.session_state.get("operator", ""),
                                        notes=f"Tab 2 Analysis - {lambda_nm}nm laser"
                                    )
                                else:
                                    response = client.upload_nta(
                                        file_path=temp_path,
                                        sample_id=tab2_sample_id,
                                        treatment=tab2_treatment,
                                        concentration_ug=tab2_concentration,
                                        preparation_method=tab2_method,
                                        operator=st.session_state.get("operator", ""),
                                        notes=f"Tab 2 Analysis"
                                    )
                                
                                st.success(f"✅ Uploaded to API: Sample ID = {response['sample_id']}")
                                st.session_state.tab2_uploaded_sample_id = response['sample_id']
                        except Exception as e:
                            st.error(f"❌ API upload failed: {str(e)}")
                            st.info("Continuing with local analysis...")
                    else:
                        st.error("Sample ID is required for API upload")
        
        df_raw, parquet_path = load_dataframe_from_uploaded(file2)
        if df_raw is None:
            st.error("Failed to read uploaded file.")
        else:
            st.markdown("**Preview of uploaded data:**")
            st.dataframe(df_raw.head(), width='stretch')

            height_cols = [c for c in df_raw.columns if str(c).strip().endswith("-H")]
            all_cols = list(df_raw.columns)
            if not height_cols:
                st.error("No '-H' height columns found in dataset. Please provide data with channels like VFSC-H, VSSC1-H, etc.")
            else:
                fsc_candidates = [c for c in height_cols if "fsc" in str(c).lower()]
                if len(fsc_candidates) > 1:
                    try:
                        medians = {c: pd.to_numeric(df_raw[c], errors="coerce").median() for c in fsc_candidates}
                        fsc_choice = max(medians, key=medians.get)  # type: ignore[arg-type]
                        st.success(f"Auto-selected FSC column: **{fsc_choice}** (highest median).")
                    except Exception:
                        fsc_choice = fsc_candidates[0]
                elif len(fsc_candidates) == 1:
                    fsc_choice = fsc_candidates[0]
                    st.info(f"Detected single FSC column: {fsc_choice}")
                else:
                    fsc_choice = height_cols[0]
                    st.info(f"No FSC-specific column found; using {fsc_choice} as FSC.")

                ssc_candidates = [c for c in height_cols if "ssc" in str(c).lower()]
                if len(ssc_candidates) > 1:
                    try:
                        medians = {c: pd.to_numeric(df_raw[c], errors="coerce").median() for c in ssc_candidates}
                        ssc_choice = max(medians, key=medians.get)  # type: ignore[arg-type]
                        st.success(f"Auto-selected SSC column: **{ssc_choice}** (highest median).")
                    except Exception:
                        ssc_choice = ssc_candidates[0]
                elif len(ssc_candidates) == 1:
                    ssc_choice = ssc_candidates[0]
                    st.info(f"Detected single SSC column: {ssc_choice}")
                else:
                    ssc_choice = height_cols[1] if len(height_cols) > 1 else height_cols[0]
                    st.info(f"No SSC-specific column found; using {ssc_choice} as SSC.")

                col1, col2 = st.columns(2)
                with col1:
                    fsc_choice_ui = st.selectbox("FSC column (auto-selected)", options=all_cols, index=all_cols.index(fsc_choice) if fsc_choice in all_cols else 0)
                with col2:
                    ssc_choice_ui = st.selectbox("SSC column (auto-selected)", options=all_cols, index=all_cols.index(ssc_choice) if ssc_choice in all_cols else 0)

                if st.button("Apply Selection", key="apply_selection"):
                    st.session_state["fsc_col_selected"] = fsc_choice_ui
                    st.session_state["ssc_col_selected"] = ssc_choice_ui
                    st.session_state["analysis_df"] = df_raw.copy()
                    st.success(f"Selection applied: FSC='{fsc_choice_ui}' | SSC='{ssc_choice_ui}'")

    else:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 50px;">
            <div style="font-size: 56px; margin-bottom: 20px;">🧬</div>
            <h3 style="color: #f8fafc; margin-bottom: 12px;">Upload Dataset</h3>
            <p style="color: #94a3b8; margin: 0;">Select FSC/SSC columns and run particle size analysis</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    run_col1, run_col2 = st.columns([1, 3])
    with run_col1:
        run_analysis = st.button("Run Analysis", key="run_analysis", use_container_width=True)
    with run_col2:
        st.write("")

    if run_analysis:
        if st.session_state.get("analysis_df") is None:
            st.error("No file applied. Upload file and click 'Apply Selection' first.")
        else:
            df = st.session_state["analysis_df"].copy()
            fsc_col = st.session_state["fsc_col_selected"]
            ssc_col = st.session_state["ssc_col_selected"]

            if fsc_col not in df.columns or ssc_col not in df.columns:
                st.error("Selected columns not present in the uploaded file. Re-apply selection.")
            else:
                with st.spinner("Running particle size analysis..."):
                    st.info(f"Running analysis with FSC='{fsc_col}' and SSC='{ssc_col}'")

                    if ignore_negative:
                        cols_to_clean = [c for c in df.columns if str(c).strip().endswith("-H")]
                        for c in cols_to_clean:
                            df[c] = pd.to_numeric(df[c], errors="coerce")  # type: ignore[assignment]
                            df.loc[df[c] < 0, c] = np.nan  # type: ignore[call-overload]

                    if drop_na:
                        before = len(df)
                        df = df.dropna(subset=[fsc_col, ssc_col])
                        after = len(df)
                        st.write(f"Dropped {before - after} rows missing FSC/SSC. {after} rows remain.")

                    df[fsc_col] = pd.to_numeric(df[fsc_col], errors="coerce")
                    df[ssc_col] = pd.to_numeric(df[ssc_col], errors="coerce")
                    
                    fsc_values = df[fsc_col].values
                    ssc_values = df[ssc_col].values
                    
                    # Vectorized division with proper handling of zeros and NaNs
                    with np.errstate(divide='ignore', invalid='ignore'):
                        measured_ratio = np.where(
                            (np.isfinite(fsc_values)) & (np.isfinite(ssc_values)) & (ssc_values != 0),
                            fsc_values / ssc_values,
                            np.nan
                        )
                    df["measured_ratio"] = measured_ratio

                    diameters = np.linspace(int(d_min), int(d_max), int(n_points))
                    angles, theoretical_ratios = build_theoretical_lookup(lambda_nm, n_particle, n_medium, fsc_range, ssc_range, diameters)

                    total = len(df)
                    t0 = time.time()
                    
                    # Show progress for building lookup (if not cached)
                    prog = st.progress(0, text="Building theoretical lookup...")
                    prog.progress(30, text="Computing particle sizes (vectorized)...")
                    
                    # Vectorized estimation - MUCH faster than row-by-row
                    estimated_diameters, matched_ratios, matched_indices = estimate_diameters_vectorized(
                        df["measured_ratio"].values,
                        theoretical_ratios,
                        diameters
                    )
                    
                    df["estimated_diameter_nm"] = estimated_diameters
                    df["matched_theoretical_ratio"] = matched_ratios
                    df["matched_idx"] = matched_indices
                    
                    prog.progress(100, text="Complete!")
                    elapsed = time.time() - t0

                    st.success(f"Processing complete in {elapsed:.1f}s - processed {total} rows.")

                    # Display stat cards
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        mean_val = df['estimated_diameter_nm'].mean()
                        st.markdown(f"""
                        <div class="stat-card">
                            <div class="stat-value">{mean_val:.1f}</div>
                            <div class="stat-label">Mean Size (nm)</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        median_val = df['estimated_diameter_nm'].median()
                        st.markdown(f"""
                        <div class="stat-card">
                            <div class="stat-value">{median_val:.1f}</div>
                            <div class="stat-label">Median Size (nm)</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        std_val = df['estimated_diameter_nm'].std()
                        st.markdown(f"""
                        <div class="stat-card">
                            <div class="stat-value">{std_val:.1f}</div>
                            <div class="stat-label">Std Dev (nm)</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col4:
                        st.markdown(f"""
                        <div class="stat-card">
                            <div class="stat-value">{total:,}</div>
                            <div class="stat-label">Total Particles</div>
                        </div>
                        """, unsafe_allow_html=True)

                    # =====================================================================
                    # USER-DEFINED SIZE RANGE DISTRIBUTION (Nov 27, 2025 requirement)
                    # Shows particle counts for each user-defined size range
                    # =====================================================================
                    if st.session_state.get("custom_size_ranges"):
                        st.markdown("---")
                        st.markdown("### 📊 Size Range Distribution")
                        st.caption("Particle counts based on your custom size ranges defined in the sidebar.")
                        
                        size_data = df['estimated_diameter_nm'].dropna()
                        
                        # Calculate counts for each range
                        range_counts = []
                        for r in st.session_state.custom_size_ranges:
                            count = len(size_data[(size_data >= r['min']) & (size_data <= r['max'])])
                            pct = (count / len(size_data) * 100) if len(size_data) > 0 else 0
                            range_counts.append({
                                "name": r['name'],
                                "range": f"{r['min']}-{r['max']} nm",
                                "count": count,
                                "percentage": pct
                            })
                        
                        # Display as stat cards (dynamic number of columns)
                        num_ranges = len(range_counts)
                        if num_ranges > 0:
                            cols = st.columns(min(num_ranges, 4))  # Max 4 columns per row
                            for i, rc in enumerate(range_counts):
                                col_idx = i % 4
                                with cols[col_idx]:
                                    st.markdown(f"""
                                    <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                                        <div class="stat-value" style="color: white;">{rc['count']:,}</div>
                                        <div class="stat-label" style="color: rgba(255,255,255,0.9);">{rc['name']}</div>
                                        <div style="font-size: 0.8rem; color: rgba(255,255,255,0.7);">{rc['range']} • {rc['percentage']:.1f}%</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        # Create summary table
                        range_df = pd.DataFrame(range_counts)
                        
                        # Add total row
                        total_counted = sum(rc['count'] for rc in range_counts)
                        uncategorized = len(size_data) - total_counted if total_counted <= len(size_data) else 0
                        
                        # Show a bar chart of size distributions
                        if len(range_counts) > 1:
                            st.markdown("**Distribution by Range:**")
                            chart_data = pd.DataFrame({
                                'Range': [rc['name'] for rc in range_counts],
                                'Count': [rc['count'] for rc in range_counts]
                            })
                            st.bar_chart(chart_data.set_index('Range'))
                        
                        # Show detailed table
                        with st.expander("📋 Detailed Size Range Statistics", expanded=False):
                            range_df_display = range_df.copy()
                            range_df_display.columns = ['Range Name', 'Size Range', 'Particle Count', 'Percentage (%)']
                            range_df_display['Percentage (%)'] = range_df_display['Percentage (%)'].apply(lambda x: f"{x:.2f}%")
                            st.dataframe(range_df_display, use_container_width=True, hide_index=True)
                            
                            if uncategorized > 0:
                                st.info(f"⚠️ {uncategorized:,} particles ({uncategorized/len(size_data)*100:.1f}%) fall outside defined ranges")
                            
                            # Size range coverage info
                            min_defined = min(r['min'] for r in st.session_state.custom_size_ranges)
                            max_defined = max(r['max'] for r in st.session_state.custom_size_ranges)
                            st.caption(f"Defined ranges cover: {min_defined}-{max_defined} nm | Data range: {size_data.min():.1f}-{size_data.max():.1f} nm")

                    # Results preview
                    preview_cols = [c for c in ["Event/EVs Sl.No", fsc_col, ssc_col, "measured_ratio", "estimated_diameter_nm"] if c in df.columns]
                    st.markdown("**Results Preview:**")
                    st.dataframe(df[preview_cols].head(200), width='stretch')

                    # Save results
                    results_parquet = os.path.join("uploads", "analysis_results.parquet")
                    try:
                        if use_pyarrow:
                            pq.write_table(pa.Table.from_pandas(df), results_parquet)  # type: ignore[name-defined]
                        else:
                            results_parquet = results_parquet.replace(".parquet", ".csv")
                            df.to_csv(results_parquet, index=False)
                    except Exception:
                        results_parquet = os.path.join("uploads", "analysis_results.csv")
                        df.to_csv(results_parquet, index=False)

                    # Download button
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)
                    csv_bytes = csv_buffer.getvalue().encode()
                    st.download_button("Download Results CSV", data=csv_bytes, file_name="estimated_sizes.csv", mime="text/csv")

                    # Plots with dark theme
                    plt.style.use('dark_background')

                    measured = df.dropna(subset=["estimated_diameter_nm", "measured_ratio"])

                    # Plot 1: Theoretical vs Measured
                    fig1, ax1 = plt.subplots(figsize=(10, 5))
                    fig1.patch.set_facecolor('#111827')
                    ax1.set_facecolor('#111827')
                    ax1.plot(diameters, theoretical_ratios, color='#00b4d8', linewidth=2, label="Theoretical ratio")
                    if not measured.empty:
                        ax1.scatter(measured["estimated_diameter_nm"], measured["measured_ratio"], s=20, alpha=0.6, c='#f72585', label="Measured events")
                    ax1.set_xlabel("Diameter (nm)", color='#f8fafc', fontsize=12)
                    ax1.set_ylabel("FSC/SSC ratio", color='#f8fafc', fontsize=12)
                    ax1.legend(facecolor='#1f2937', edgecolor='#374151', labelcolor='#f8fafc')
                    ax1.tick_params(colors='#94a3b8')
                    for spine in ax1.spines.values():
                        spine.set_color('#374151')
                    ax1.grid(True, alpha=0.2, color='#374151')
                    st.pyplot(fig1)
                    plt.close()

                    # Plot 2: Histogram
                    fig2, ax2 = plt.subplots(figsize=(10, 5))
                    fig2.patch.set_facecolor('#111827')
                    ax2.set_facecolor('#111827')
                    ax2.hist(measured["estimated_diameter_nm"].dropna(), bins=40, color='#00b4d8', edgecolor='#0096c7', alpha=0.85)
                    ax2.set_xlabel("Estimated diameter (nm)", color='#f8fafc', fontsize=12)
                    ax2.set_ylabel("Counts", color='#f8fafc', fontsize=12)
                    ax2.set_title("Particle Size Distribution", color='#f8fafc', fontsize=14, fontweight='bold')
                    ax2.tick_params(colors='#94a3b8')
                    for spine in ax2.spines.values():
                        spine.set_color('#374151')
                    ax2.grid(True, alpha=0.2, color='#374151')

                    plot_path = os.path.join("images", "particle_size_histogram.png")
                    fig2.savefig(plot_path, dpi=150, bbox_inches='tight', facecolor='#111827')
                    st.pyplot(fig2)
                    plt.close()

                    # Plot 3: FSC vs SSC scatter
                    if fsc_col in df.columns and ssc_col in df.columns:
                        fig3, ax3 = plt.subplots(figsize=(8, 6))
                        fig3.patch.set_facecolor('#111827')
                        ax3.set_facecolor('#111827')
                        scatter = ax3.scatter(df[fsc_col], df[ssc_col], s=8, alpha=0.5, c='#7c3aed')
                        ax3.set_xlabel(fsc_col, color='#f8fafc', fontsize=12)
                        ax3.set_ylabel(ssc_col, color='#f8fafc', fontsize=12)
                        ax3.set_title("FSC vs SSC", color='#f8fafc', fontsize=14, fontweight='bold')
                        ax3.tick_params(colors='#94a3b8')
                        for spine in ax3.spines.values():
                            spine.set_color('#374151')
                        ax3.grid(True, alpha=0.2, color='#374151')
                        st.pyplot(fig3)
                        plt.close()

                    # Plot 4: Diameter vs SSC
                    if "estimated_diameter_nm" in df.columns and ssc_col in df.columns:
                        fig4, ax4 = plt.subplots(figsize=(10, 5))
                        fig4.patch.set_facecolor('#111827')
                        ax4.set_facecolor('#111827')
                        ax4.scatter(df["estimated_diameter_nm"], df[ssc_col], s=8, alpha=0.5, c='#10b981')
                        ax4.set_xlabel("Estimated Diameter (nm)", color='#f8fafc', fontsize=12)
                        ax4.set_ylabel(ssc_col, color='#f8fafc', fontsize=12)
                        ax4.set_title(f"Estimated Diameter vs {ssc_col}", color='#f8fafc', fontsize=14, fontweight='bold')
                        ax4.tick_params(colors='#94a3b8')
                        for spine in ax4.spines.values():
                            spine.set_color('#374151')
                        ax4.grid(True, alpha=0.2, color='#374151')
                        st.pyplot(fig4)
                        plt.close()

                    st.success(f"Histogram saved to: {plot_path}")

                    # Save session results
                    st.session_state["last_analysis_df"] = df.copy()
                    st.session_state["last_theoretical"] = {"diameters": diameters, "ratios": theoretical_ratios}

    # Show previous results if present
    if st.session_state.get("last_analysis_df") is not None:
        st.markdown("---")
        st.info("Previous analysis available in this session. You can re-download or re-plot.")
        if st.button("Show Previous Results"):
            df_prev = st.session_state["last_analysis_df"]
            preview_cols = [c for c in ["Event/EVs Sl.No", st.session_state.get("fsc_col_selected"), st.session_state.get("ssc_col_selected"), "measured_ratio", "estimated_diameter_nm"] if c in df_prev.columns]
            st.dataframe(df_prev[preview_cols].head(200), width='stretch')


# -------------------------
# TAB 3: Nanoparticle Tracking Analysis
# -------------------------

with tab3:
    st.markdown(
        """
        <div style='text-align:center;'>
            <h3 style='color:#00b4d8;'>⚛ Nanoparticle Tracking Analysis</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    # CSS Animations
    st.markdown(
        """
        <style>
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0px); }
        }
        .animated-section {
            animation: fadeIn 0.7s ease-in-out;
        }
        .tree-ul {
            list-style-type: none;
            margin-left: 1rem;
            line-height: 1.6;
        }
        .tree-ul li::before {
            content: "├── ";
            margin-right: 0.4rem;
        }
        .tree-ul li:last-child::before {
            content: "└── ";
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    uploaded_file_nta = st.file_uploader(
        "📎 Upload NTA Data File",
        type=["csv", "xlsx", "xls", "json", "parquet"],
        help="Supported formats: CSV, Excel, JSON, Parquet"
    )

    # Show Best Practices above upload if file not uploaded yet
    if uploaded_file_nta:
        st.markdown(
            "<div class='animated-section'>"
            "<h4 style='color:#00b4d8;'>🔼 🧠 Best Practices</h4>"
            "</div>",
            unsafe_allow_html=True
        )

        # Optionally show details in expanders
        with st.expander("🛠️ Machine Calibration", expanded=True):
            st.markdown(
                """
                <ul style="line-height:1.8;">
                    <li><b>Maintenance:</b> Cell cleaning should be performed with <b>100% acetone weekly</b>.</li>
                    <li><b>Sample Handling:</b> All samples must be passed through a <b>0.2 μm filter</b> and <b>vortexed before dilution</b>.</li>
                </ul>
                """,
                unsafe_allow_html=True
            )

        with st.expander("🧪 Sample Preparation", expanded=True):
            st.markdown(
                """
                <ul style="line-height:1.8;">
                    <li><b>Dilution:</b> Optimal number of particles per frame should be <b>50–100</b>.</li>
                    <li><b>Buffer Options:</b>
                        <ul>
                            <li>1️⃣ PBS pH 7.4 <em>(fresh stock, filtered through 0.02 μm filter)</em></li>
                            <li>2️⃣ HPLC grade water <em>(filtered through 0.02 μm filter)</em></li>
                        </ul>
                    </li>
                    <li><b>Capture Strategy:</b> Minimum of <b>3 cycles</b> and <b>11 positions</b> for statistical accuracy.</li>
                </ul>
                """,
                unsafe_allow_html=True
            )

        # Reconfirm upload
        st.success("📁 File uploaded successfully!")
        st.info("✔ You may now proceed with NTA analysis.")
    else:
        # Show Best Practices collapsed if no file yet
        st.info("📤 Please upload an NTA file to show best practices.")

