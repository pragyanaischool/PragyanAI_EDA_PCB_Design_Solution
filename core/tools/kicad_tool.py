import pcbnew
import os
import json
from typing import Dict, List

class KiCadLayoutTool:
    """
    Automates the physical PCB layout process using the KiCad Scripting API.
    Used by Placement and Routing Agents to manipulate .kicad_pcb files.
    """

    def __init__(self, pcb_file_path: str = None):
        self.pcb_file_path = pcb_file_path
        if pcb_file_path and os.path.exists(pcb_file_path):
            self.board = pcbnew.LoadBoard(pcb_file_path)
        else:
            self.board = pcbnew.BOARD()

    def apply_placement(self, placement_data: List[Dict]):
        """
        Updates component positions based on AI-generated coordinates.
        Input: [{'designator': 'U1', 'x': 100, 'y': 100, 'rotation': 90}, ...]
        """
        for comp in placement_data:
            module = self.board.FindFootprintByReference(comp['designator'])
            if module:
                # KiCad uses nanometers or internal units (IU)
                # Converting mm to internal units
                pos = pcbnew.VECTOR2I_MM(comp['x'], comp['y'])
                module.SetPosition(pos)
                module.SetOrientation(pcbnew.EDA_ANGLE(comp['rotation'], pcbnew.DEGREES_T))
        
        self.save()
        return {"success": True, "message": f"Placed {len(placement_data)} components."}

    def set_board_boundary(self, width_mm: float, height_mm: float, margin_mm: float = 5.0):
        """
        Draws the Edge.Cuts layer based on required dimensions.
        """
        edge_layer = pcbnew.Edge_Cuts
        # Define rectangle corners
        points = [
            (0, 0), (width_mm, 0), 
            (width_mm, height_mm), (0, height_mm), (0, 0)
        ]
        
        for i in range(len(points) - 1):
            start = pcbnew.VECTOR2I_MM(points[i][0], points[i][1])
            end = pcbnew.VECTOR2I_MM(points[i+1][0], points[i+1][1])
            segment = pcbnew.PCB_SHAPE(self.board)
            segment.SetShape(pcbnew.SHAPE_T_SEGMENT)
            segment.SetStart(start)
            segment.SetEnd(end)
            segment.SetLayer(edge_layer)
            self.board.Add(segment)
            
        self.save()

    def run_drc(self, output_report: str):
        """
        Invokes the Design Rule Checker.
        Note: Deep DRC typically requires the kicad-cli for comprehensive reports.
        """
        # Save board state before DRC
        self.save()
        # In modern KiCad 8, CLI is preferred for DRC automation:
        cmd = f"kicad-cli pcb drc --output {output_report} {self.pcb_file_path}"
        os.system(cmd)
        return {"report_path": output_report}

    def save(self):
        """Persists changes to the .kicad_pcb file."""
        if self.pcb_file_path:
            pcbnew.SaveBoard(self.pcb_file_path, self.board)
        else:
            raise ValueError("No file path provided to save the board.")

# Helper function for Agents
def auto_place_components(pcb_path: str, placement_json: str):
    layout = KiCadLayoutTool(pcb_path)
    data = json.loads(placement_json)
    return layout.apply_placement(data)
  
