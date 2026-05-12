import json
import os
import csv
from typing import List, Dict

class BOMAgent:
    """
    The Implementation Cluster: BOM Agent.
    Validates part availability and generates the final Bill of Materials.
    """

    def __init__(self, mapping_path: str = "design/lib/mapping.json"):
        self.mapping_path = mapping_path
        with open(self.mapping_path, 'r') as f:
            self.mapping = json.load(f)
        
        self.bom_list = []

    def fetch_live_data(self, mpn: str) -> Dict:
        """
        Simulates an API call to Octopart or LCSC to get live pricing/stock.
        In a production environment, this uses requests.get() with an API key.
        """
        # Mocking the API response for the PragyanAI pipeline
        return {
            "MPN": mpn,
            "Stock": 5000,
            "Price_USD": 0.12,
            "Status": "Active"
        }

    def process_design(self, netlist_components: List[Dict]):
        """
        Matches design aliases (e.g., 'res_0603_10k') to real-world parts.
        """
        print("🛒 BOMAgent: Matching design components to supply chain data...")
        
        for comp in netlist_components:
            alias = comp.get("alias")
            designator = comp.get("ref")
            
            # Lookup metadata in mapping.json
            part_info = self.mapping.get(alias)
            
            if not part_info:
                print(f"⚠️ Warning: No mapping found for {alias}. Manual entry required.")
                continue

            # Fetch live supply chain status
            live_status = self.fetch_live_data(part_info.get("mpn"))

            self.bom_list.append({
                "Designator": designator,
                "Value": comp.get("value", "N/A"),
                "MPN": part_info.get("mpn"),
                "Manufacturer": part_info.get("manufacturer"),
                "Package": part_info.get("footprint"),
                "Price": live_status["Price_USD"],
                "Stock": live_status["Stock"],
                "Status": live_status["Status"]
            })

    def export_csv(self, output_path: str = "design/output/bom.csv"):
        """Exports the verified BOM to a CSV for factory upload."""
        if not self.bom_list:
            print("❌ Error: BOM is empty. Process the design first.")
            return

        keys = self.bom_list[0].keys()
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', newline='') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.bom_list)
            
        print(f"✅ BOMAgent: Exported {len(self.bom_list)} items to {output_path}")

# --- Example Logic for the Implementation Cluster ---
if __name__ == "__main__":
    # Mocking data that would normally come from the SKiDLAgent/Netlist
    designed_components = [
        {"ref": "U1", "alias": "esp32_wroom_32e"},
        {"ref": "U2", "alias": "ams1117_3v3"},
        {"ref": "R1", "alias": "res_0603_10k", "value": "10k"},
        {"ref": "C1", "alias": "cap_0805_22uf", "value": "22uF"}
    ]

    agent = BOMAgent()
    agent.process_design(designed_components)
    agent.export_csv()
  
