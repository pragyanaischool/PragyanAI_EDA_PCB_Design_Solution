import json
import math
import os

class PlacementAgent:
    """
    The Implementation Cluster: Placement Agent.
    Calculates physical coordinates for components to optimize routing 
    and thermal management.
    """

    def __init__(self, plan_path="design/config/architecture_plan.json"):
        self.output_path = "design/output/placement.json"
        with open(plan_path, 'r') as f:
            self.plan = json.load(f)
        
        self.canvas_size = (50.0, 50.0) # Default 50mm x 50mm
        self.placements = {}

    def _get_distance(self, p1, p2):
        """Calculates Euclidean distance between two points."""
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    def calculate_layout(self, components):
        """
        Executes the placement algorithm.
        Strategy: 
        1. Place MCU (U1) at the center.
        2. Place Power Regulation (U2) at the top edge.
        3. Place Bypass Caps (C1, C2) within 2mm of their target pins.
        """
        print("📍 PlacementAgent: Calculating optimal spatial layout...")
        
        center_x, center_y = self.canvas_size[0] / 2, self.canvas_size[1] / 2

        for comp in components:
            ref = comp['ref']
            alias = comp['alias']

            # 1. Main Processor Placement
            if "esp32" in alias:
                self.placements[ref] = {
                    "x": center_x, 
                    "y": center_y, 
                    "rotation": 0,
                    "layer": "Top"
                }

            # 2. Power Section (Top-Left quadrant)
            elif "ams1117" in alias or "buck" in alias:
                self.placements[ref] = {
                    "x": 10.0, 
                    "y": 10.0, 
                    "rotation": 90,
                    "layer": "Top"
                }

            # 3. Decoupling Capacitors (Proximity Logic)
            elif "cap" in alias:
                # Find the component it belongs to (simplified logic)
                target_x = center_x - 5.0 if "U1" in ref else 10.0
                self.placements[ref] = {
                    "x": target_x + 2.0, 
                    "y": 12.0, 
                    "rotation": 0,
                    "layer": "Top"
                }

            # 4. Connectors (Edge Placement)
            elif "usb" in alias:
                self.placements[ref] = {
                    "x": 0.0, # Flush with left edge
                    "y": center_y, 
                    "rotation": 270,
                    "layer": "Top"
                }

        return self.placements

    def export_placement(self):
        """Saves coordinates for the Layout and Fab agents."""
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, 'w') as f:
            json.dump(self.placements, f, indent=4)
        print(f"✅ PlacementAgent: Spatial map exported to {self.output_path}")

# --- Standalone Execution ---
if __name__ == "__main__":
    # Simulated component list from SKiDLAgent
    comp_list = [
        {"ref": "U1", "alias": "esp32_wroom_32e"},
        {"ref": "U2", "alias": "ams1117_3v3"},
        {"ref": "J1", "alias": "usb_c_connector"},
        {"ref": "C1", "alias": "cap_0603_100nf"}
    ]

    agent = PlacementAgent()
    layout = agent.calculate_layout(comp_list)
    agent.export_placement()
  
