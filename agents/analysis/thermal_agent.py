import json
import os
from typing import Dict, List

class ThermalAgent:
    """
    Analysis Cluster: Thermal Agent.
    Calculates temperature gradients and predicts hotspots based on 
    power consumption and PCB physical properties (Stackup & Area).
    """

    def __init__(self, 
                 placement_path: str = "design/output/placement.json",
                 stackup_path: str = "design/config/stackup.json"):
        
        self.placement_path = placement_path
        self.stackup_path = stackup_path
        self.report_path = "design/output/thermal_analysis.json"
        
        # Internal Constants
        self.AMBIENT_TEMP = 25.0  # Celsius
        self.MAX_SAFE_TEMP = 85.0 # Typical Industrial Limit
        
    def _calculate_theta_ja(self, area_mm2: float, cu_weight_oz: float) -> float:
        """
        Simplified Thermal Resistance (Theta-JA) calculation.
        Lower values mean better heat dissipation.
        """
        # Heuristic: More copper and more area = lower thermal resistance
        base_resistance = 150.0  # K/W for a small 0603 footprint
        reduction_factor = (area_mm2 * cu_weight_oz) / 100.0
        return max(30.0, base_resistance - reduction_factor)

    def analyze_system(self, component_power_draw: Dict[str, float]) -> Dict:
        """
        Main Analysis Loop.
        Input: Dict mapping Designators (e.g., 'U1') to Power (Watts).
        """
        print("🔥 ThermalAgent: Running thermal simulation...")
        
        # 1. Load Environmental Data
        with open(self.stackup_path, 'r') as f:
            stackup = json.load(f)
        
        # Extract copper weight from Top layer
        top_cu = next(l for l in stackup['layers'] if l['name'] == 'F.Cu')
        cu_weight = top_cu.get('weight_oz', 1.0)

        results = {
            "summary": "PASS",
            "max_board_temp": 0.0,
            "hotspots": []
        }

        # 2. Iterate through power-consuming components
        total_board_power = 0.0
        
        for ref, power in component_power_draw.items():
            # Estimate footprint area (In production, pulled from FootprintAnalyzer)
            footprint_area = 50.0 # mm2 (estimated for an LDO)
            
            # Calculate Temperature Rise: Delta_T = Power * Theta_JA
            theta_ja = self._calculate_theta_ja(footprint_area, cu_weight)
            delta_t = power * theta_ja
            component_temp = self.AMBIENT_TEMP + delta_t
            
            total_board_power += power
            
            # Log results for this component
            comp_data = {
                "designator": ref,
                "power_watts": power,
                "predicted_temp": round(component_temp, 2),
                "status": "SAFE" if component_temp < self.MAX_SAFE_TEMP else "CRITICAL"
            }
            
            if comp_data["status"] == "CRITICAL":
                results["summary"] = "FAIL"
            
            results["hotspots"].append(comp_data)
            results["max_board_temp"] = max(results["max_board_temp"], component_temp)

        # 3. Save Report
        self._save_report(results)
        return results

    def _save_report(self, data: Dict):
        os.makedirs(os.path.dirname(self.report_path), exist_ok=True)
        with open(self.report_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"✅ ThermalAgent: Analysis saved to {self.report_path}")

# --- Standalone Verification ---
if __name__ == "__main__":
    # Simulated power consumption from Analysis Agent
    # U1 (ESP32) @ 0.2W, U2 (AMS1117) @ 0.8W (e.g. dropping 12V to 3.3V at high load)
    power_data = {
        "U1": 0.2,
        "U2": 0.8  
    }
    
    agent = ThermalAgent()
    analysis = agent.analyze_system(power_data)
    
    print(f"🌡️ Max Board Temperature: {analysis['max_board_temp']:.2f}°C")
    if analysis['summary'] == "FAIL":
        print("⚠️ WARNING: High thermal stress detected. Consider a Buck converter or larger copper pours.")
      
