import json
import re
from typing import Dict, Any

class RequirementsAgent:
    """
    The Planning Cluster: Requirements Agent.
    Transforms raw PRD (Product Requirement Document) text into 
    structured design constraints for the Architecture Agent.
    """

    def __init__(self):
        # The schema that following agents (Arch, SKiDL) expect
        self.design_spec = {
            "project_metadata": {
                "name": "Untitled_Project",
                "version": "1.0.0"
            },
            "power": {
                "input_v": 5.0,        # Default to USB 5V
                "logic_v": 3.3,        # Default to 3.3V logic
                "max_current_ma": 500  # Default current limit
            },
            "mcu": {
                "family": "ESP32",     # Default choice
                "required": True
            },
            "interfaces": [],          # I2C, SPI, UART, etc.
            "peripherals": [],         # Sensors, LEDs, Buttons
            "physical": {
                "max_width_mm": 100,
                "max_height_mm": 100
            }
        }

    def _extract_voltage(self, text: str):
        """Regex helper to find voltage requirements."""
        v_match = re.search(r'(\d+\.?\d*)\s*[Vv]', text)
        if v_match:
            self.design_spec["power"]["input_v"] = float(v_match.group(1))

    def _extract_mcu(self, text: str):
        """Identifies requested MCU families."""
        families = ["ESP32", "STM32", "RP2040", "AVR", "nRF52"]
        for family in families:
            if family.lower() in text.lower():
                self.design_spec["mcu"]["family"] = family

    def _extract_interfaces(self, text: str):
        """Identifies communication protocols."""
        protocols = ["I2C", "SPI", "UART", "USB-C", "CAN", "RS485"]
        for proto in protocols:
            if proto.lower() in text.lower():
                self.design_spec["interfaces"].append(proto)

    def parse(self, prd_text: str) -> Dict[str, Any]:
        """
        Main entry point. In a production environment, this method 
        would call an LLM (e.g., Gemini-3-Flash) to perform complex 
        extraction. This version uses rule-based logic for reliability.
        """
        print(f"🧠 ReqAgent: Analyzing project requirements...")
        
        self._extract_voltage(prd_text)
        self._extract_mcu(prd_text)
        self._extract_interfaces(prd_text)
        
        # Extract Peripherals (Simple keyword matching)
        peripherals = ["LED", "OLED", "Sensor", "Button", "Switch"]
        for p in peripherals:
            if p.lower() in prd_text.lower():
                self.design_spec["peripherals"].append(p)

        return self.design_spec

    def save_spec(self, filename="design/config/active_spec.json"):
        """Persists the extracted requirements for other agents."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(self.design_spec, f, indent=4)
        print(f"💾 ReqAgent: Design specification saved to {filename}")

# --- Example Usage ---
if __name__ == "__main__":
    import os
    
    agent = RequirementsAgent()
    user_input = "I want a small ESP32 board powered by 12V with an OLED display and I2C sensors."
    
    # Process
    spec = agent.parse(user_input)
    
    # Display Result
    print(json.dumps(spec, indent=2))
    
    # Save for Architecture Agent
    # agent.save_spec()

  
