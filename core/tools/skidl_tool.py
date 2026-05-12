import sys
import os
from io import StringIO
from skidl import *

class SkidlTool:
    """
    Compiler and Validator for Python-based PCB Schematics.
    Wraps SKiDL functionality for AI agent consumption.
    """

    def __init__(self, project_name: str = "ai_generated_pcb"):
        self.project_name = project_name
        # Reset SKiDL state for a fresh design
        default_circuit.reset()
        # Set KiCad as the target output format
        set_default_tool(KICAD)

    def run_erc(self, skidl_code: str):
        """
        Executes the provided SKiDL code and runs Electrical Rule Checks.
        Returns a report of floating pins, shorts, and conflicts.
        """
        # Capture stdout to gather ERC reports
        old_stdout = sys.stdout
        sys.stdout = erc_buffer = StringIO()

        try:
            # Execute the AI-generated code in a controlled namespace
            exec_globals = {"Net": Net, "Part": Part, "ERC": ERC, "generate_netlist": generate_netlist}
            exec(skidl_code, exec_globals)
            
            # Perform Electrical Rule Check
            ERC()
            
            sys.stdout = old_stdout
            return {
                "success": True,
                "report": erc_buffer.getvalue(),
                "error": None
            }
        except Exception as e:
            sys.stdout = old_stdout
            return {
                "success": False, 
                "report": erc_buffer.getvalue(),
                "error": str(e)
            }

    def export_netlist(self, skidl_code: str, output_path: str):
        """
        Compiles the SKiDL code and exports a KiCad-compatible Netlist file.
        """
        try:
            default_circuit.reset()
            exec_globals = {"Net": Net, "Part": Part, "generate_netlist": generate_netlist}
            exec(skidl_code, exec_globals)
            
            # Generate the netlist file (.net)
            generate_netlist(file_ = output_path)
            
            return {"success": True, "path": output_path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_bom(self, output_path: str):
        """
        Generates a Bill of Materials based on the parts instantiated in the circuit.
        """
        try:
            generate_xml(file_ = output_path)
            return {"success": True, "path": output_path}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global Helper for Agents
def validate_circuit_logic(code: str):
    tool = SkidlTool()
    return tool.run_erc(code)
