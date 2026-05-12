import streamlit as st
import os
import pandas as pd
from datetime import datetime

# --- Import Orchestrator & Agents ---
from orchestrator import PragyanOrchestrator

# --- Configuration ---
st.set_page_config(
    page_title="PragyanAI Autonomous EDA",
    page_icon="🤖",
    layout="wide"
)

# --- Global State Management ---
if 'project_id' not in st.session_state:
    st.session_state.project_id = f"PRJ-{datetime.now().strftime('%y%m%d-%H%M')}"
if 'current_step' not in st.session_state:
    st.session_state.current_step = "Planning"
if 'logs' not in st.session_state:
    st.session_state.logs = []

# --- Custom Styling ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# --- Navigation Sidebar ---
with st.sidebar:
    st.image("https://via.placeholder.com/150?text=PragyanAI", width=120)
    st.title("Studio Workflow")
    activity = st.radio(
        "Go to Activity:",
        ["🎯 Project Planning", "🔨 Implementation", "🔬 Lab Analysis", "📦 Fulfillment"]
    )
    st.divider()
    st.info(f"Active Project: **{st.session_state.project_id}**")

# --- Activity 1: Planning ---
if activity == "🎯 Project Planning":
    st.header("Step 1: AI Requirements & Architecture")
    col_input, col_out = st.columns([1, 1])
    
    with col_input:
        st.subheader("Design Prompt")
        user_prompt = st.text_area(
            "Describe your hardware in plain English:",
            "A high-efficiency ESP32 module with 12V input, I2C headers, and a battery charging circuit.",
            height=200
        )
        if st.button("Initialize Agents", type="primary"):
            st.session_state.logs.append(f"Planning Agent started for: {user_prompt}")
            st.success("Planning complete! Check Architecture Plan.")

    with col_out:
        st.subheader("Architecture Preview")
        # In production, this pulls from design/config/architecture_plan.json
        mock_arch = {
            "Power Tree": "12V -> Buck (5V) -> LDO (3.3V)",
            "MCU": "ESP32-S3-WROOM-1",
            "Interfaces": ["I2C", "UART", "ADC"],
            "Layers": 4
        }
        st.json(mock_arch)

# --- Activity 2: Implementation ---
elif activity == "🔨 Implementation":
    st.header("Step 2: Circuit Construction & Sourcing")
    
    col_bom, col_place = st.columns(2)
    
    with col_bom:
        st.subheader("BOM Audit")
        # Mocking data from bom_agent.py
        bom_df = pd.DataFrame({
            "Ref": ["U1", "U2", "C1", "R1"],
            "Part": ["ESP32-WROOM", "MP2315", "22uF", "10k"],
            "Status": ["In Stock", "In Stock", "In Stock", "In Stock"],
            "Price (USD)": [3.40, 1.20, 0.05, 0.01]
        })
        st.table(bom_df)
    
    with col_place:
        st.subheader("Placement Strategy")
        st.code("""
        // placement.json
        "U1": {"x": 25.0, "y": 25.0, "rot": 0},
        "J1": {"x": 0.0, "y": 12.5, "rot": 270}
        """, language="json")
        st.info("Component spacing checked against FootprintAnalyzer.")

# --- Activity 3: Lab Analysis ---
elif activity == "🔬 Lab Analysis":
    st.header("Step 3: Physics-Based Verification")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Max Temperature", "48.2°C", "-2.1°C")
    m2.metric("Signal Integrity", "98.4%", "+1.2%")
    m3.metric("DRC Errors", "0", "Critical")
    
    st.subheader("Thermal Gradient Map")
    # In production, this would render a heatmap based on thermal_agent results
    st.image("https://via.placeholder.com/800x300.png?text=PCB+Thermal+Heatmap+Simulation", use_column_width=True)
    
    with st.expander("View SI/PI Testbench Logs"):
        st.text("Executing Transient Analysis on +3.3V Rail...\nStabilization: 12ms\nRipple: 15mV (PASS)")

# --- Activity 4: Fulfillment ---
elif activity == "📦 Fulfillment":
    st.header("Step 4: Manufacturing Pack & Documentation")
    
    st.info("All validation gates have been PASSED. Files are ready for production.")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.subheader("Production Files")
        st.download_button("📦 Download Gerber ZIP", "mock_data", file_name="Gerbers_RevA.zip")
        st.caption("Standard ODB++ & Drill files included.")
        
    with c2:
        st.subheader("Technical Docs")
        st.download_button("📄 Design Validation Report", "mock_data", file_name="DVR_Report.md")
        st.caption("Includes Thermal and SI/PI traces.")

    with c3:
        st.subheader("Factory Handover")
        st.button("🚀 Push to JLCPCB API", disabled=True)
        st.caption("Direct factory API integration (V2 Feature).")

# --- Activity Logger (Bottom of all pages) ---
st.divider()
with st.expander("📜 System Master Logs"):
    for log in st.session_state.logs:
        st.text(log)
        
