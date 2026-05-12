import os
import sys
import json
from datetime import datetime

# Import Agent Clusters
from agents.planning.req_agent import RequirementsAgent
from agents.planning.arch_agent import ArchitectureAgent
from agents.implementation.skidl_agent import SKiDLAgent
from agents.implementation.bom_agent import BOMAgent
from agents.implementation.placement_agent import PlacementAgent
from agents.analysis.si_pi_agent import SI_PI_Agent
from agents.analysis.thermal_agent import ThermalAgent
from agents.analysis.drc_agent import DRCAgent
from agents.outputs.fab_agent import FabAgent
from agents.outputs.doc_agent import DocAgent

class PragyanOrchestrator:
    """
    The Central Nervous System of the PragyanAI EDA Framework.
    Manages sequential agent execution and cross-agent data validation.
    """
    
    def __init__(self, project_name="PragyanAI_Project"):
        self.project_name = project_name
        self.start_time = datetime.now()
        print(f"🚀 {self.project_name}: Orchestrator initialized.")

    def run_full_lifecycle(self, user_prompt: str):
        """
        Executes the 4-Cluster Pipeline from prompt to Gerber files.
        """
        try:
            # --- STAGE 1: PLANNING ---
            print("\n--- [CLUSTER 1: PLANNING] ---")
            req_agent = RequirementsAgent()
            specs = req_agent.parse(user_prompt)
            req_agent.save_spec()

            arch_agent = ArchitectureAgent()
            arch_plan = arch_agent.run()
            arch_agent.save_architecture()

            # --- STAGE 2: IMPLEMENTATION ---
            print("\n--- [CLUSTER 2: IMPLEMENTATION] ---")
            skidl_agent = SKiDLAgent()
            skidl_agent.construct_circuit()
            skidl_agent.generate_netlist()

            # Simulated list of components for BOM and Placement
            # In production, these are parsed from the generated netlist
            components = [
                {"ref": "U1", "alias": "esp32_wroom_32e"},
                {"ref": "U2", "alias": "ams1117_3v3"},
                {"ref": "C1", "alias": "cap_0805_22uf", "value": "22uF"}
            ]

            bom_agent = BOMAgent()
            bom_agent.process_design(components)
            bom_agent.export_csv()

            placement_agent = PlacementAgent()
            placement_agent.calculate_layout(components)
            placement_agent.export_placement()

            # --- STAGE 3: ANALYSIS ---
            print("\n--- [CLUSTER 3: ANALYSIS] ---")
            
            # Thermal Analysis
            thermal = ThermalAgent()
            # Mocked power consumption for analysis
            power_data = {"U1": 0.2, "U2": 0.8} 
            thermal_report = thermal.analyze_system(power_data)

            # DRC Validation
            drc = DRCAgent()
            # Mocked physical layout stats from the placement agent results
            layout_stats = {"min_trace_width": 0.2, "min_clearance": 0.2, "min_via_drill": 0.4}
            drc_report = drc.run_validation(layout_stats)

            if drc_report["overall_status"] == "FAIL":
                print("🛑 CRITICAL: DRC Failed. Aborting fabrication.")
                return False

            # --- STAGE 4: FULFILLMENT ---
            print("\n--- [CLUSTER 4: FULFILLMENT] ---")
            
            fab_agent = FabAgent(self.project_name)
            fab_pack_path = fab_agent.prepare_factory_package()

            doc_agent = DocAgent(self.project_name)
            report_path = doc_agent.generate_dvr()

            self._finalize_summary(fab_pack_path, report_path)

        except Exception as e:
            print(f"❌ Orchestrator Error: {str(e)}")
            return False

    def _finalize_summary(self, zip_path, doc_path):
        duration = datetime.now() - self.start_time
        print("\n" + "="*40)
        print("✅ PROJECT COMPLETE")
        print(f"⏱️ Total Execution Time: {duration}")
        print(f"📦 Manufacturing Pack: {zip_path}")
        print(f"📄 Validation Report: {doc_path}")
        print("="*40)

if __name__ == "__main__":
    # Example Input for your Venture Studio
    PRD = "Design a 12V input PCB for an ESP32 monitoring node with I2C sensor headers."
    
    orchestrator = PragyanOrchestrator("Industrial_Node_V1")
    orchestrator.run_full_lifecycle(PRD)
  
