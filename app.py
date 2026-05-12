import streamlit as st
import os
import json
from orchestrator import PragyanOrchestrator
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="PragyanAI | Autonomous EDA Studio",
    page_icon="⚡",
    layout="wide"
)

# --- Session State Initialization ---
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'process_complete' not in st.session_state:
    st.session_state.process_complete = False

def logger(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {message}")

# --- Sidebar: Project Settings ---
st.sidebar.image("https://via.placeholder.com/150?text=PragyanAI", width=150)
st.sidebar.title("Settings")
project_name = st.sidebar.text_input("Project Name", value="SmartNode_V1")
target_fab = st.sidebar.selectbox("Target Factory", ["JLCPCB", "PCBWay", "Custom"])

# --- Main UI ---
st.title("🚀 Autonomous Hardware Agent")
st.markdown("""
    Generate manufacture-ready PCB designs from natural language prompts.
    *Powered by the PragyanAI Multi-Agent EDA Framework.*
""")

prompt = st.text_area(
    "Enter Design Requirements (PRD):",
    placeholder="e.g., A 5V ESP32 board with an OLED display, two I2C sensors, and 0603 components.",
    height=150
)

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("Start Autonomous Design", type="primary"):
        if not prompt:
            st.error("Please enter a design prompt.")
        else:
            st.session_state.logs = []
            logger("Initializing Orchestrator...")
            
            # Initialize the Brain
            studio = PragyanOrchestrator(project_name)
            
            # Execute Pipeline
            with st.spinner("Agents are working..."):
                success = studio.run_full_lifecycle(prompt)
                
            if success != False:
                st.session_state.process_complete = True
                logger("Pipeline finished successfully.")
            else:
                st.error("Pipeline failed during analysis. Check logs.")

    # Display Live Logs
    st.subheader("Agent Activity Logs")
    log_box = st.empty()
    log_text = "\n".join(st.session_state.logs)
    log_box.code(log_text if log_text else "Awaiting start...")

with col2:
    st.subheader("Design Outputs")
    if st.session_state.process_complete:
        st.success("Design Validated & Packaged!")
        
        # Download Buttons for Cluster 4 Outputs
        fab_path = f"design/output/{project_name}_FAB_RevA.zip" # Path logic should match FabAgent
        report_path = "design/output/docs/DVR_Report.md"

        if os.path.exists(report_path):
            with open(report_path, "r") as f:
                st.download_button("📂 Download Validation Report", f, file_name=f"{project_name}_Report.md")
        
        # In a real app, you would provide the actual ZIP file generated
        st.info("The manufacturing ZIP (Gerbers, Drill, BOM) is ready for pickup in the `design/output` directory.")
        
        # Visual Preview (Mockup of the generated board)
        st.image("https://via.placeholder.com/600x400.png?text=PCB+Layout+Preview", caption="Automated Placement Preview")
    else:
        st.write("Outputs will appear here once the agents complete the validation cycle.")

# --- Footer ---
st.divider()
st.caption(f"© 2026 Pragyan SmartAI Technology LLP | System Time: {datetime.now().strftime('%Y-%m-%d')}")
