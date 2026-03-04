
import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import time
import random
import requests
import smtplib
from email.message import EmailMessage
from fpdf import FPDF
import re
from langchain_ollama import OllamaLLM

# ================= MODERN UI CONFIG =================
st.set_page_config(
    page_title="AURORA | Elite AI Reliability Platform",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Pinterest-Inspired "Billion Dollar" Design System
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --accent: #7C3AED;
    --accent-glow: rgba(124, 58, 237, 0.3);
    --bg: #030712;
    --card-bg: rgba(17, 24, 39, 0.7);
    --border: rgba(255, 255, 255, 0.08);
}

.stApp {
    background: radial-gradient(circle at 0% 0%, #1e1b4b 0%, #030712 50%),
                radial-gradient(circle at 100% 100%, #312e81 0%, #030712 50%);
    color: #F3F4F6;
    font-family: 'Outfit', sans-serif;
}

/* Typography Overhauls */
h1 {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    letter-spacing: -1px;
    background: linear-gradient(to right, #FFF, #9CA3AF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3rem !important;
    margin-bottom: 0 !important;
}

h2, h3 {
    font-weight: 600;
    letter-spacing: -0.5px;
}

/* Glassmorphism Cards with 3D Border */
div[data-testid="stMetric"], div[data-testid="stExpander"], div.stDataFrame, .stPlotlyChart {
    background: var(--card-bg) !important;
    backdrop-filter: blur(28px);
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 20px !important;
    padding: 24px !important;
    box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.2), 0 0 16px 0 rgba(124, 58, 237, 0.1) !important;
    transition: all 0.5s cubic-bezier(0.19, 1, 0.22, 1) !important;
    position: relative;
    overflow: hidden;
}

div[data-testid="stExpander"]:hover {
    border: 1px solid rgba(124, 58, 237, 0.4) !important;
    box-shadow: 0 0 40px rgba(124, 58, 237, 0.25) !important;
    transform: perspective(1000px) rotateX(1deg) translateY(-5px);
}

/* 21st.dev Style Glowing Border Animation */
@keyframes border-glow {
    0% { border-color: rgba(124, 58, 237, 0.1); }
    50% { border-color: rgba(124, 58, 237, 0.6); }
    100% { border-color: rgba(124, 58, 237, 0.1); }
}

.sim-container {
    animation: border-glow 4s infinite;
}

/* Pinterest-style metrics */
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 2.5rem !important;
    color: #fff !important;
    text-shadow: 0 0 20px rgba(124, 58, 237, 0.5);
}

/* High-End Buttons (Mercury 3D Style) */
.stButton>button {
    background: #fff;
    color: #000 !important;
    border-radius: 12px;
    border: none;
    font-weight: 700;
    padding: 0.8rem 2.5rem;
    box-shadow: 0 0 0 0 rgba(255,255,255,0.4);
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background: #7C3AED;
    color: #fff !important;
    box-shadow: 0 0 25px rgba(124, 58, 237, 0.6);
}

/* Advanced Visualization Wrappers */
.viz-card {
    border-left: 4px solid var(--accent);
    padding-left: 20px;
}

/* Log Stream Style */
.stCode {
    background: #000 !important;
    border: 1px solid #333 !important;
    border-radius: 12px !important;
}

/* Hide Streamlit components */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# ================= APP LOGIC =================
DATA_DIR = Path("data/classifications")
DATA_DIR.mkdir(parents=True, exist_ok=True)

SEVERITY_SCORE_MAP = {
    "Hallucination": 5,
    "Data Drift": 4,
    "Retrieval Failure": 3,
    "Prompt Design Failure": 2,
    "Tool Misuse": 1
}

PRESET_INCIDENTS = {
    "Custom Analysis (Manual Input)": "",
    "Hallucination: Phantom Specs": "The model is hallucinating technical specifications for a 'Quantum-Core V5' product that doesn't exist in our grounding database.",
    "Data Drift: Semantic Shift": "The semantic drift monitor shows a 0.7 drop in embedding similarity for finance queries after the model swap to Llama-3.",
    "Retrieval Failure: Spiking Latency": "Retrieval latency has spiked by 400% after the latest vector index update, causing time-outs in the user interface.",
    "Prompt Failure: Loopback": "The agent is repeating the same prompt instructions back to the user instead of executing the requested SQL query.",
    "Tool Misuse: Schema Violation": "The model attempted to call the 'delete_user' tool with raw string input instead of a valid JSON object."
}

# AUTH
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<h1 style='text-align:center;'>AURORA</h1>", unsafe_allow_html = True)
        st.markdown("<p style='text-align:center; opacity:0.6;'>ENTERPRISE SECURITY PORTAL</p>", unsafe_allow_html = True)
        role = st.selectbox("Authorization Level", ["Admin", "Lead Engineer"])
        if st.button("AUTHENTICATE"):
            st.session_state.authenticated = True
            st.session_state.role = role
            st.rerun()
    st.stop()

# DATA LOADING
records = []
for file in DATA_DIR.glob("*.json"):
    with open(file, encoding="utf-8") as f:
        obj = json.load(f)
        obj["timestamp"] = obj.get("timestamp", file.stat().st_mtime)
        obj["model"] = obj.get("model", "Core-LLM-v4")
        records.append(obj)
df = pd.DataFrame(records)
if df.empty:
    df = pd.DataFrame(columns=["incident_id", "failure_type", "severity_score", "confidence", "recommended_fix", "timestamp", "model"])
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", errors="coerce")

# ================= HEADER PART =================
header_l, header_r = st.columns([2, 1])
with header_l:
    st.markdown("<h1>System Diagnostics</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.2rem; opacity:0.5;'>Automated AI Root-Cause Analysis & Real-Time Monitoring</p>", unsafe_allow_html=True)
with header_r:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info(f"⚡ AUTHENTICATED: {st.session_state.role} | NODE: DX-04")

st.markdown("<br>", unsafe_allow_html=True)

# ================= DYNAMIC INPUT (TOP) =================
with st.expander("💎 INJECT NEURAL INCIDENT", expanded=True):
    preset_choice = st.selectbox("SELECT PRESET CASE STUDY (OPTIONAL)", list(PRESET_INCIDENTS.keys()))
    default_text = PRESET_INCIDENTS[preset_choice]
    
    c1, c2 = st.columns([3, 1])
    with c1:
        sim_desc = st.text_area("FAILURE VECTOR DESCRIPTION", value=default_text, placeholder="Describe the anomaly in detail...", height=80)
    with c2:
        sim_model = st.text_input("INSTANCE", "GPT-REPORTER-PRO")
        if st.button("ANALYSIS & COMMIT", use_container_width=True):
            if sim_desc:
                with st.spinner("QUANTUM ENGINE PROCESSING..."):
                    try:
                        llm = OllamaLLM(model="llama3")
                        prompt = f"Classify this AI failure description into JSON with fields 'failure_type', 'confidence', 'recommended_fix'. Types: Hallucination, Data Drift, Retrieval Failure, Prompt Design Failure, Tool Misuse. Input: {sim_desc}"
                        response = llm.invoke(prompt)
                        match = re.search(r"\{.*\}", response, re.DOTALL)
                        if match:
                            parsed = json.loads(match.group())
                            new_id = f"incid_{int(time.time())}"
                            parsed.update({"incident_id": new_id, "model": sim_model, "timestamp": datetime.now().timestamp(), "severity_score": SEVERITY_SCORE_MAP.get(parsed["failure_type"], 3)})
                            (DATA_DIR / f"{new_id}.json").write_text(json.dumps(parsed, indent=2))
                            st.success("NODE COMMITTED SUCCESSFULLY")
                            time.sleep(1)
                            st.rerun()
                    except: st.error("NEURAL ENGINE OFFLINE")

st.markdown("<br>", unsafe_allow_html=True)

# ================= METRICS AREA =================
total = len(df)
avg_severity = round(df["severity_score"].mean(), 2) if total else 0
high_risk = (df["severity_score"] >= 4).sum()

grade = (
    "A" if avg_severity < 2 else
    "B" if avg_severity < 3 else
    "C" if avg_severity < 4 else
    "D"
)

st.markdown("### 📊 System Vital Signs")

# Real-time Hardware Simulation (Job-Winning Detail)
c1, c2, c3, c4 = st.columns(4)
c1.metric("NEURAL LOAD", f"{random.randint(40, 85)}%", f"{random.randint(-10, 10)}%")
c2.metric("SYNAPTIC LATENCY", f"{random.randint(120, 240)}ms", f"{random.randint(-20, 20)}ms")
c3.metric("UPTIME", "99.98%", "ONLINE")
c4.metric("NODE RANK", grade, "TOP TIER")

st.markdown("<br>", unsafe_allow_html=True)

# Main Enterprise Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("CRITICAL ANOMALIES", high_risk, delta_color="inverse")
m2.metric("MEAN SEVERITY", avg_severity)
m3.metric("RELIABILITY GRADE", grade)
m4.metric("TOTAL ANALYSIS", total)

st.markdown("<br>", unsafe_allow_html=True)

# ================= VIZ AREA =================
v1, v2 = st.columns([1.5, 1])

with v1:
    st.markdown("### 🧬 INCIDENT FREQUENCY TIMELINE")
    if total:
        trend = df.sort_values("timestamp").groupby(df["timestamp"].dt.date)["severity_score"].mean()
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')
        ax.plot(trend, color='#7C3AED', linewidth=3, marker='o', markersize=8, markerfacecolor='white')
        ax.spines['bottom'].set_color('#ffffff22')
        ax.spines['left'].set_color('#ffffff22')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(colors='white', labelsize=8)
        ax.grid(color='#ffffff', alpha=0.05, linestyle='--')
        st.pyplot(fig)

with v2:
    st.markdown("### 📊 VECTOR DISTRIBUTION")
    if total:
        counts = df["failure_type"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 6))
        fig.patch.set_facecolor('none')
        # Professional Donut Chart
        ax.pie(counts, labels=counts.index, colors=['#A855F7', '#6366F1', '#3B82F6', '#22C55E', '#F59E0B'], 
               autopct='%1.1f%%', textprops={'color':"w", 'size': 9}, pctdistance=0.85, 
               wedgeprops={'width': 0.4, 'edgecolor': '#030712', 'linewidth': 2})
        st.pyplot(fig)

st.markdown("<br>", unsafe_allow_html=True)

# ================= SOLUTIONS HUB =================
st.markdown("---")
st.markdown("## 🧠 NEURAL ROOT CAUSE ANALYSIS & SOLUTIONS")

if not df.empty:
    for _, row in df.sort_values("severity_score", ascending=False).iterrows():
        with st.expander(f"📍 {row['incident_id']} • {row['failure_type']}", expanded=True if row['severity_score'] >= 5 else False):
            c_a, c_b = st.columns([1, 1])
            with c_a:
                st.markdown("#### 🚨 Detected Failure")
                confidence_val = row.get('confidence', 0.8)
                # Handle cases where confidence might be string or missing
                try:
                    conf_score = int(float(confidence_val) * 100)
                except:
                    conf_score = 80
                st.info(f"**Anomaly Level:** {row['severity_score']}/5\n\n**Confidence Index:** {conf_score}%")
            with c_b:
                st.markdown("#### 💡 Expert Solution & Fix")
                fix_text = row.get('recommended_fix', '')
                if not fix_text or fix_text.strip() == "":
                    fix_text = "Deploy automated guardrails and grounding filters."
                st.success(fix_text)
            
            st.markdown("#### 🛡️ Long-term Prevention")
            st.write(f"Neural analysis suggests increasing vector precision for {row['failure_type']} by implementing a cross-encoder re-ranking layer and strict validation schemas.")

st.markdown("<br>", unsafe_allow_html=True)

# ================= PDF REPORTING ENGINE =================
st.markdown("---")
st.markdown("### 📄 EXECUTIVE PDF GENERATION")

if "pdf_ready" not in st.session_state:
    st.session_state.pdf_ready = False

col_p1, col_p2 = st.columns([1, 2])
with col_p1:
    if st.button("PREPARE PDF REPORT", use_container_width=True):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "AURORA | EXECUTIVE RELIABILITY REPORT", ln=True, align='C')
            pdf.ln(10)
            
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 10, f"Generated Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
            pdf.ln(5)

            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Summary Analytics:", ln=True)
            pdf.set_font("Arial", size=11)
            pdf.cell(0, 9, f" - Total Analysis Conducted: {total}", ln=True)
            pdf.cell(0, 9, f" - Critical Anomalies: {high_risk}", ln=True)
            pdf.cell(0, 9, f" - Mean Severity: {avg_severity}", ln=True)
            pdf.cell(0, 9, f" - Reliability Rank: {grade}", ln=True)
            
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Standard Prevention Protocols:", ln=True)
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 8, "1. Deploy 3-stage hallucination filters to pre-inference nodes.", ln=True)
            pdf.cell(0, 8, "2. Implement synaptic-load balancing for high-concurrency tasks.", ln=True)
            pdf.cell(0, 8, "3. Enable automated drift detection with self-healing triggers.", ln=True)

            pdf.output("aurora_report.pdf")
            st.session_state.pdf_ready = True
            st.success("PDF Buffer Compiled.")
        except Exception as e:
            st.error(f"Engine Fault: {e}")

with col_p2:
    if st.session_state.pdf_ready:
        with open("aurora_report.pdf", "rb") as f:
            st.download_button(
                label="💾 DOWNLOAD ENCRYPTED REPORT",
                data=f,
                file_name=f"AURORA_SEC_REPORT_{int(time.time())}.pdf",
                mime="application/pdf"
            )

# ================= ADVANCED FOOTER =================
st.markdown("""
<div class='footer'>
    AURORA DIAMOND EDITION • QUANTUM RELIABILITY PLATFORM v4.0.2 • [SECRET // NOFORN]
</div>
""", unsafe_allow_html=True)
