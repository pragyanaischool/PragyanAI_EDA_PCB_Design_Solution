import json

class RequirementsAgent:
    """Parses natural language requirements into hardware specs."""
    def __init__(self):
        self.spec_template = {
            "mcu_family": "ESP32",
            "voltage_input": 5.0,
            "interfaces": [],
            "max_dimensions": [50, 50]
        }

    def parse_prd(self, prd_text):
        # In production, this would use an LLM call to extract entities
        # For now, it outputs the structured JSON for the implementation cluster
        print("📝 Requirements Agent: Extracting hardware constraints...")
        return self.spec_template

# Example Logic
if __name__ == "__main__":
    agent = RequirementsAgent()
    specs = agent.parse_prd("Build a 5V ESP32 board with USB-C and I2C.")
  
