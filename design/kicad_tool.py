import os
import subprocess

class KiCadAutomator:
    """
    Utility to automate the KiCad backend. 
    Converts Netlists to PCBs and exports Gerbers.
    """
    def __init__(self, project_name, output_dir="design/output"):
        self.project_name = project_name
        self.output_dir = output_dir

    def generate_outputs(self):
        """Generates Gerbers, Drill, and BoM via KiCad CLI."""
        print(f"📦 Generating manufacturing pack for {self.project_name}...")
        
        # Paths to KiCad CLI (standard in KiCad 6+)
        commands = [
            ["kicad-cli", "pcb", "export", "gerbers", "-o", f"{self.output_dir}/gerber/", f"{self.project_name}.kicad_pcb"],
            ["kicad-cli", "pcb", "export", "drill", "-o", f"{self.output_dir}/drill/", f"{self.project_name}.kicad_pcb"]
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, check=True)
            except Exception as e:
                print(f"❌ Error running KiCad CLI: {e}")

# Global instance for the Orchestrator
kicad_bridge = KiCadAutomator("PragyanAI_V1")
