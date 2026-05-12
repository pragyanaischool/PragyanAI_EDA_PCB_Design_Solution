import os
import json
from datetime import datetime

# Import Agent Pods
from agents.planning.req_agent import RequirementsAgent
from agents.planning.arch_agent import ArchitectureAgent
from agents.implementation.skidl_agent import SKiDLAgent
from agents.implementation.bom_agent import BOMAgent
from agents.implementation.placement_agent import PlacementAgent
from agents.analysis.thermal_agent import ThermalAgent
from agents.analysis.drc_agent import DRCAgent
from agents.outputs.fab_agent import FabAgent
from agents.outputs.doc_agent import DocAgent

class PragyanOrchestrator:
    """
    Orchestrator for the PragyanAI Autonomous EDA Framework.
    Manages the lifecycle from PRD to Gerber generation.
    """

    def __init__(self, project_name="PragyanAI_Project"):
        self.project_name = project_name
        self.output_root = "design/output"
        self.config_root = "design/config"
        
        # Ensure directory structure exists
        for path in [self.output_root, self.config_root, "design/output/docs"]:
            os.makedirs(path, exist_ok=True)

    def run_planning(self, prompt: str):
        """Activity 1: Parse PRD and generate System Architecture."""
        print(f"🎯 [Planning] Starting for {self.project_name}...")
        
        req = RequirementsAgent()
        specs = req.parse(prompt)
        req.save_spec()

        arch = ArchitectureAgent()
        plan = arch.run()
        arch.save_architecture()
        
        return plan

    def run_implementation(self):
        """Activity 2: Generate Netlist, BOM, and Placement Map."""
        print(f"🔨 [Implementation] Building hardware logic...")
        
        # 1. Logic Construction
        skidl_gen = SKiDLAgent()
        skidl_gen.construct_circuit()
        skidl_gen.generate_netlist()

        # 2. Sourcing
        # In a full flow, components are parsed from the netlist
        components = [
            {"ref": "U1", "alias": "esp32_wroom_32e"},
            {"ref": "U2", "alias": "ams1117_3v3"},
            {"ref": "C1", "alias": "cap_0805_22uf"}
        ]
        
        bom = BOMAgent()
        bom.process_design(components)
        bom.export_csv()

        # 3. Spatial Layout
        place = PlacementAgent()
        layout = place.calculate_layout(components)
        place.export_placement()
        
        return layout

    def run_analysis(self):
        """Activity 3: Verify physics (Thermal, DRC, SI/PI)."""
        print(f"🔬 [Analysis] Commencing hardware validation...")
        
        # Thermal Check
        thermal = ThermalAgent()
        power_draw = {"U1": 0.25, "U2": 0.75} # Mocked from electrical specs
        t_report = thermal.analyze_system(power_draw)

        # DRC Check
        drc = DRCAgent()
        # Mocked stats from PlacementAgent and Stackup
        stats = {"min_trace_width": 0.2, "min_clearance": 0.2, "min_via_drill": 0.3}
        drc_report = drc.run_validation(stats)

        return {"thermal": t_report, "drc": drc_report}

    def run_fulfillment(self):
        """Activity 4: Package Gerbers and Documentation."""
        print(f"📦 [Fulfillment] Generating manufacturing assets...")
        
        fab = FabAgent(self.project_name)
        zip_path = fab.prepare_factory_package()

        doc = DocAgent(self.project_name)
        report_path = doc.generate_dvr()

        return {"fab_zip": zip_path, "report_md": report_path}

    def execute_full_pipeline(self, prompt: str):
        """Runs all stages in sequence for one-click automation."""
        self.run_planning(prompt)
        self.run_implementation()
        analysis = self.run_analysis()
        
        if analysis['drc']['overall_status'] == "PASS":
            return self.run_fulfillment()
        else:
            print("🛑 Pipeline stopped: DRC Failure.")
            return None

if __name__ == "__main__":
    # Test execution
    studio = PragyanOrchestrator("Demo_Project")
    result = studio.execute_full_pipeline("A simple ESP32 breakout with USB-C and 3.3V LDO.")
    if result:
        print(f"🚀 Design Successful: {result['fab_zip']}")
        
  
