import os

class MechanicalValidator:
    """
    Checks if component heights exceed the enclosure limits 
    provided in the project constraints.
    """
    def __init__(self, model_dir="design/lib/3d_models/"):
        self.model_dir = model_dir

    def check_height_clearance(self, component_list, max_height_mm=10.0):
        """
        Scans a list of components and flags any that have 3D models 
        exceeding the maximum allowed height.
        """
        violations = []
        for comp in component_list:
            model_path = os.path.join(self.model_dir, comp['model_path'])
            
            # In a real tool, this would parse the STEP file metadata
            # Here we simulate a height check based on file naming/metadata
            comp_height = comp.get('measured_height', 0.0) 
            
            if comp_height > max_height_mm:
                violations.append({
                    "designator": comp['ref'],
                    "height": comp_height,
                    "limit": max_height_mm
                })
        
        return violations

# Usage Example:
if __name__ == "__main__":
    validator = MechanicalValidator()
    # Simulated data from the Layout Agent
    board_components = [
        {"ref": "U1", "model_path": "ICs/ESP32.step", "measured_height": 3.3},
        {"ref": "J1", "model_path": "Connectors/USB_C.step", "measured_height": 12.5}
    ]
    
    errors = validator.check_height_clearance(board_components, max_height_mm=10.0)
    for err in errors:
        print(f"❌ MECHANICAL ERROR: {err['designator']} is {err['height']}mm tall (Limit: {err['limit']}mm)")
