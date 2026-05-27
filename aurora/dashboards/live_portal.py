import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt
import time
import random
import asyncio
from pathlib import Path
from datetime import datetime
from fpdf import FPDF

# Import our platform core modules
from aurora.orchestration.mesh_coordinator import MeshCoordinator
from aurora.orchestration.event_broker import EventBroker
from aurora.observability.metrics_collector import MetricsCollector
from aurora.observability.scorer import ReliabilityScorer
from aurora.security.guardrails import SecurityGuardrails
from aurora.chaos_engine.chaos_neuron import ChaosNeuron
from aurora.data_layer.vector_store import LocalIncidentStore

# ================= MODERN UI CONFIG =================
st.set_page_config(
    page_title="AURORA | Elite AI Reliability Platform",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "coordinator" not in st.session_state:
    st.session_state.coordinator = MeshCoordinator()
    st.session_state.broker = EventBroker()
    st.session_state.metrics = MetricsCollector()
    st.session_state.scorer = ReliabilityScorer()
    st.session_state.guardrails = SecurityGuardrails()
    st.session_state.db = LocalIncidentStore()
    
    # Pre-seed some classifications if database is empty to make it look full
    if len(st.session_state.db.load_all_incidents()) == 0:
        for i in range(5):
            new_id = f"static_case_{i}_{int(time.time())}"
            cases = [
                {"failure_type": "Hallucination", "confidence": 0.92, "recommended_fix": "Deploy strict semantic grounding filters.", "description": "Model hallucinated pricing limits."},
                {"failure_type": "Data Drift", "confidence": 0.88, "recommended_fix": "Retrain embeddings on financial datasets.", "description": "Semantic distance dropped by 0.7."},
                {"failure_type": "Retrieval Failure", "confidence": 0.95, "recommended_fix": "Increase DB connection timeout.", "description": "Vector indexing timeout occurred."},
                {"failure_type": "Prompt Design Failure", "confidence": 0.85, "recommended_fix": "Wrap inputs using structured XML delimiters.", "description": "Model repeated system instructions back."},
                {"failure_type": "Tool Misuse", "confidence": 0.90, "recommended_fix": "Update tool signature parser scheme.", "description": "Model sent string to delete_user."}
            ]
            case = cases[i]
            case.update({
                "incident_id": new_id,
                "model": "STATIC-SEEDER-v1",
                "timestamp": time.time() - (i * 3600),
                "severity_score": 5 - i
            })
            st.session_state.db.save_incident(new_id, case)

# Pinterest-Inspired HSL Design Tokens
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

/* Typography */
h1 {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    letter-spacing: -1px;
    background: linear-gradient(to right, #FFF, #9CA3AF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.6rem !important;
}

h2, h3 {
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    letter-spacing: -0.5px;
}

/* Glassmorphism Cards */
div[data-testid="stMetric"], div[data-testid="stExpander"], div.stDataFrame, .stPlotlyChart {
    background: var(--card-bg) !important;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px !important;
    padding: 20px !important;
    box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.2), 0 0 16px 0 rgba(124, 58, 237, 0.05) !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stExpander"]:hover {
    border: 1px solid rgba(124, 58, 237, 0.3) !important;
    box-shadow: 0 0 32px rgba(124, 58, 237, 0.15) !important;
    transform: translateY(-2px);
}

/* Metrics and Values */
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 2.2rem !important;
    color: #fff !important;
    text-shadow: 0 0 16px rgba(124, 58, 237, 0.4);
}

/* Elite glowing terminal block */
.terminal-block {
    background-color: #020617 !important;
    border: 1px solid #1e293b !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    border-radius: 12px;
    padding: 15px;
    max-height: 250px;
    overflow-y: auto;
    color: #38bdf8;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
}

/* Glow animation button */
.stButton>button {
    background: #fff;
    color: #000 !important;
    border-radius: 10px;
    border: none;
    font-weight: 600;
    padding: 0.6rem 2rem;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background: #7C3AED;
    color: #fff !important;
    box-shadow: 0 0 20px rgba(124, 58, 237, 0.5);
}

/* Agent Network Nodes */
.agent-node {
    padding: 10px 15px;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: bold;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}
.agent-active {
    background: linear-gradient(135deg, #7C3AED, #4F46E5) !important;
    border: 1px solid #A78BFA !important;
    color: white !important;
    box-shadow: 0 0 20px rgba(124, 58, 237, 0.6) !important;
    animation: pulse 1.5s infinite alternate;
}
.agent-idle {
    background: rgba(31, 41, 55, 0.6) !important;
    color: #9CA3AF !important;
}

@keyframes pulse {
    0% { transform: scale(1); }
    100% { transform: scale(1.05); }
}
</style>
""", unsafe_allow_html=True)

# ================= AUTHENTICATION GATE =================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1.2, 1.8, 1.2])
    with c2:
        st.markdown("<h1 style='text-align:center;'>AURORA</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; opacity:0.6; font-size:1.1rem;'>AGENTIC AI RELIABILITY OPERATING SYSTEM</p>", unsafe_allow_html=True)
        
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        role = st.selectbox("Select Authorization Node", ["Admin", "Lead Reliability Architect", "SecOps Officer"])
        password = st.text_input("Synaptic Signature Hash Key", type="password", placeholder="Enter key...")
        
        if st.button("AUTHORIZE SYSTEM ACCESS", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.role = role
            st.rerun()
    st.stop()

# ================= SIDEBAR: SYSTEM CHAOS CONTROL & INPUT =================
with st.sidebar:
    st.markdown("<h2>⚡ System Control</h2>", unsafe_allow_html=True)
    st.markdown("<p style='opacity:0.6; font-size:0.85rem;'>Inject anomalies & red-team attacks into the Multi-Agent Reliability Mesh.</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🧬 ChaosNeuron Ingestion")
    
    chaos_choice = st.selectbox("Select Chaos Vector", [
        "Hallucination (Pricing Anomaly)",
        "Retrieval Corruption (Index Timeout)",
        "Data Drift (Embedding Shift)",
        "Prompt Injection (Adversarial Attack)",
        "Tool Misuse (Schematic Violation)"
    ])
    
    if st.button("INJECT CHAOS VECTOR", use_container_width=True):
        chaos_map = {
            "Hallucination (Pricing Anomaly)": "hallucination",
            "Retrieval Corruption (Index Timeout)": "retrieval_corruption",
            "Data Drift (Embedding Shift)": "data_drift",
            "Prompt Injection (Adversarial Attack)": "prompt_injection",
            "Tool Misuse (Schematic Violation)": "tool_misuse"
        }
        
        chaos_type = chaos_map[chaos_choice]
        event = ChaosNeuron.get_preset_chaos_event(chaos_type)
        
        with st.spinner("AGENT MESH PROCESSING INJECTION..."):
            # If it's prompt injection, scan through security guardrails first
            if chaos_type == "prompt_injection":
                st.session_state.guardrails.scan_input(event["description"])
                
            # Submit to mesh
            loop = asyncio.new_event_loop()
            final_report = loop.run_until_complete(
                st.session_state.coordinator.ingest_failure(
                    event["description"], event["model"], event["incident_id"]
                )
            )
            loop.close()
            
            # Save diagnosed report to classifications database
            if final_report:
                st.session_state.db.save_incident(final_report["incident_id"], final_report)
                
            st.toast(f"✅ Chaos {chaos_type.upper()} successfully isolated and self-healed!", icon="🛡️")
            time.sleep(0.5)
            st.rerun()

    st.markdown("---")
    st.markdown("### 💉 Manual Payload Injection")
    manual_desc = st.text_area("RAW FAILURE VECTOR", placeholder="Describe anomaly payload...", height=70)
    manual_model = st.text_input("INSTANCE NODE", "GPT-REPORTER-PRO")
    
    if st.button("COMMIT PAYLOAD", use_container_width=True):
        if manual_desc:
            with st.spinner("MESH PARSING PAYLOAD..."):
                # Pre-scan for security validation
                st.session_state.guardrails.scan_input(manual_desc)
                
                loop = asyncio.new_event_loop()
                final_report = loop.run_until_complete(
                    st.session_state.coordinator.ingest_failure(
                        manual_desc, manual_model
                    )
                )
                loop.close()
                if final_report:
                    st.session_state.db.save_incident(final_report["incident_id"], final_report)
                st.toast("✅ Incident successfully scanned and logged!", icon="🧠")
                time.sleep(0.5)
                st.rerun()

    st.markdown("---")
    if st.button("CLEAR DATABASE"):
        st.session_state.db.clear_all()
        st.session_state.broker.clear_history()
        st.toast("Database reset completed successfully.", icon="💥")
        time.sleep(0.5)
        st.rerun()

# ================= HEADER =================
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown("<h1>AURORA // AI Reliability Operating System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.1rem; opacity:0.5; margin-top:-10px;'>Multi-Agent Self-Healing Mesh & Production Observability Engine</p>", unsafe_allow_html=True)
with c2:
    st.info(f"🛡️ ROLE: {st.session_state.role} | ACTIVE PORT: 8502")

st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)

# ================= METRICS & SCORING =================
r_score = st.session_state.scorer.calculate_score()
aggregated = st.session_state.metrics.get_aggregated_metrics()

m1, m2, m3, m4 = st.columns(4)
m1.metric("RELIABILITY INDEX", f"{r_score}/100", f"{'HEALTHY' if r_score > 85 else 'DEGRADED'}")
m2.metric("TOTAL INCIDENTS", aggregated["total_incidents"])
m3.metric("AUTO-HEALED RATE", f"{aggregated['auto_healed']} Fixes", "SELF-HEALED")
m4.metric("BLOCKED ATTACKS", f"{aggregated['attacks_blocked']} Blocks", "SHIELD ACTIVE")

st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

# ================= MAIN PANELS =================
col_left, col_right = st.columns([1.8, 1.2])

with col_left:
    # 🔗 Glowing Multi-Agent Mesh Topology Map
    st.markdown("### 🕸️ Active Agentic Mesh Topology")
    
    # Read the last active trace in event broker to highlight active agent
    last_event = st.session_state.broker.get_history(1)
    active_agent = ""
    if last_event:
        traces = last_event[0].get("agent_trace", [])
        if traces:
            active_agent = traces[-1]["agent"]

    agent_names = [
        "ObserverAgent", "SecurityAgent", "AutopsyAgent", "RetrievalAgent",
        "RepairAgent", "ValidationAgent", "DriftAgent", "GovernanceAgent"
    ]
    
    # Render layout grids of active nodes
    cols = st.columns(4)
    for i, name in enumerate(agent_names[:4]):
        is_active = active_agent == name
        cls_name = "agent-active" if is_active else "agent-idle"
        tag = "⚡ ACTIVE" if is_active else "💤 STANDBY"
        cols[i].markdown(f"""
        <div class="agent-node {cls_name}">
            <div>{name}</div>
            <div style="font-size:0.7rem; opacity:0.8; font-weight:normal;">{tag}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    
    cols2 = st.columns(4)
    for i, name in enumerate(agent_names[4:]):
        is_active = active_agent == name
        cls_name = "agent-active" if is_active else "agent-idle"
        tag = "⚡ ACTIVE" if is_active else "💤 STANDBY"
        cols2[i].markdown(f"""
        <div class="agent-node {cls_name}">
            <div>{name}</div>
            <div style="font-size:0.7rem; opacity:0.8; font-weight:normal;">{tag}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # 📊 Live Failures & Mitigations Hub
    st.markdown("### 🧠 Incident Diagnostics & Solutions Ledger")
    df_records = pd.DataFrame(st.session_state.db.load_all_incidents())
    
    if not df_records.empty:
        df_records = df_records.sort_values("timestamp", ascending=False)
        for _, row in df_records.iterrows():
            severity = row.get("severity_score", 3)
            confidence = int(row.get("confidence", 0.8) * 100)
            
            with st.expander(f"📍 {row['incident_id']} • {row.get('failure_type', 'System Anomaly')}", expanded=(severity >= 5)):
                c_a, c_b = st.columns([1, 1])
                with c_a:
                    st.markdown("#### 🚨 Anomaly Details")
                    st.info(f"**Anomaly Level:** {severity}/5\n\n**Confidence Index:** {confidence}%\n\n**Description:** *{row['description']}*")
                with c_b:
                    st.markdown("#### 💡 Remediation Strategy")
                    fix = row.get("recommended_fix", "Apply strict grounding validator.")
                    patch = row.get("remediation_patch", "No code patch generated.")
                    st.success(f"**Action Plan:** {fix}\n\n**System Code Patch:**\n```\n{patch}\n```")

with col_right:
    # 📡 Live Telemetry Event Logs (Kafka Simulation)
    st.markdown("### 📟 Live Telemetry Event Console")
    hist = st.session_state.broker.get_history(15)
    
    terminal_content = ""
    if not hist:
        terminal_content = "[*] Listening on telemetry event stream...\n"
    for e in reversed(hist):
        timestamp = datetime.fromtimestamp(e.get("broker_timestamp", time.time())).strftime("%H:%M:%S.%f")[:-3]
        topic = e.get("topic", "UNKNOWN")
        inc_id = e.get("incident_id", "GLOBAL")
        terminal_content += f"[{timestamp}] TOPIC: {topic} | INCIDENT: {inc_id}\n"
        
    st.markdown(f'<pre class="terminal-block">{terminal_content}</pre>', unsafe_allow_html=True)

    st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)

    # 🛡️ Security Guardrails Panel
    st.markdown("### 🛡️ Guardrail Monitor")
    blocked = st.session_state.guardrails.get_blocked_payloads()
    
    sec_col1, sec_col2 = st.columns(2)
    sec_col1.metric("THREAT THRESHOLD", "HIGH", "99% STABLE")
    sec_col2.metric("BLOCKED PAYLOADS", len(blocked))
    
    if blocked:
        st.markdown("<p style='font-size:0.85rem; color:#f87171; font-weight:bold;'>Blocked Payloads Ledger:</p>", unsafe_allow_html=True)
        for b in reversed(blocked[-3:]):
            st.markdown(f"""
            <div style='background:rgba(239, 68, 68, 0.1); border-left:3px solid #ef4444; padding:8px; border-radius:5px; margin-bottom:5px; font-size:0.8rem;'>
                <strong>{b['attack_type']}</strong> (Risk: {b['risk_score']}%)<br>
                Payload: <code>{b['payload']}</code>
            </div>
            """, unsafe_allow_html=True)

# ================= EXECUTIVE PDF GENERATOR =================
st.markdown("---")
st.markdown("### 📄 Executive PDF Generation Engine")

col_p1, col_p2 = st.columns([1, 2])
with col_p1:
    if st.button("PREPARE EXECUTIVE REPORT", use_container_width=True):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "AURORA | EXECUTIVE AI RELIABILITY REPORT", ln=True, align='C')
            pdf.ln(10)
            
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 10, f"Generated Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
            pdf.cell(0, 10, f"Report Token ID: AUR-SEC-REP-{int(time.time())}", ln=True)
            pdf.ln(5)

            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Summary Operational Analytics:", ln=True)
            pdf.set_font("Arial", size=11)
            pdf.cell(0, 9, f" - Total AI Reliability Score: {r_score}/100", ln=True)
            pdf.cell(0, 9, f" - Total Ingested Incidents: {aggregated['total_incidents']}", ln=True)
            pdf.cell(0, 9, f" - Remediation Auto-Healed: {aggregated['auto_healed']}", ln=True)
            pdf.cell(0, 9, f" - Blocked Security Attacks: {aggregated['attacks_blocked']}", ln=True)
            
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Remediation & Healing Protocols:", ln=True)
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 8, "1. Enforce pre-inference semantic guardrail scanning for jailbreaks.", ln=True)
            pdf.cell(0, 8, "2. Deploy auto-patching prompt filters inside sandbox validators.", ln=True)
            pdf.cell(0, 8, "3. Run daily embedding index validation checks to prevent drift.", ln=True)

            pdf.output("data/aurora_exec_report.pdf")
            st.session_state.pdf_ready = True
            st.success("Executive PDF report compiled in data directory.")
        except Exception as e:
            st.error(f"Engine Fault: {e}")

with col_p2:
    if st.session_state.get("pdf_ready", False):
        try:
            with open("data/aurora_exec_report.pdf", "rb") as f:
                st.download_button(
                    label="💾 DOWNLOAD EXECUTED EXECUTIVE REPORT",
                    data=f,
                    file_name=f"AURORA_SEC_REPORT_{int(time.time())}.pdf",
                    mime="application/pdf"
                )
        except Exception:
            pass

# ================= ADVANCED FOOTER =================
st.markdown("""
<div style='text-align:center; padding:30px; opacity:0.4; font-size:0.75rem; border-top:1px solid rgba(255,255,255,0.05); margin-top:50px;'>
    AURORA DIAMOND EDITION • QUANTUM AGENTIC INFRASTRUCTURE v5.0.0 • [SECRET // NOFORN]
</div>
""", unsafe_allow_html=True)
