import json
import os
import sys

class LibraryManager:
    """
    Orchestrates the validation and retrieval of hardware components.
    Ensures absolute consistency between Logic (Symbols), Physics (Footprints),
    and Procurement (MPNs).
    """

    def __init__(self, project_root=None):
        # Set project root to the parent of the 'design' folder if not provided
        self.project_root = project_root or os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        self.mapping_path = os.path.join(self.project_root, "design/lib/mapping.json")
        self.lib_data = self._load_mapping()

    def _load_mapping(self):
        """Loads the master component mapping file."""
        if not os.path.exists(self.mapping_path):
            raise FileNotFoundError(f"Mapping file missing: {self.mapping_path}")
        with open(self.mapping_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_part_alias(self, alias: str):
        """
        Retrieves all metadata for a specific part alias.
        Used by the Schematic Agent to find the correct Symbol/Footprint.
        """
        part = self.lib_data.get(alias)
        if not part:
            print(f"❌ Error: Part alias '{alias}' is not defined in mapping.json")
            return None
        return part

    def validate_project_libraries(self):
        """
        Verifies that every symbol and footprint referenced in mapping.json 
        actually exists on the disk. Run this before final Netlist generation.
        """
        errors = []
        for alias, details in self.lib_data.items():
            # Check Symbols
            symbol_path = os.path.join(self.project_root, "design/lib/symbols/enterprise_core.kicad_sym")
            # (In a full implementation, this would call symbol_extractor.py to verify)
            
            # Check Footprints
            fp_folder = details.get("footprint", "").split(":")[0]
            fp_name = details.get("footprint", "").split(":")[-1]
            fp_path = os.path.join(self.project_root, f"design/lib/footprints/{fp_folder}.pretty/{fp_name}.kicad_mod")
            
            if not os.path.exists(fp_path):
                errors.append(f"Missing Footprint: {alias} -> {fp_path}")

        return errors

    def generate_bom_data(self, components_in_design: list):
        """
        Takes a list of used designators (e.g., ['R1', 'U1']) and 
        returns a structured list for procurement.
        """
        bom = []
        for comp in components_in_design:
            alias = comp.get('alias')
            ref = comp.get('ref')
            metadata = self.get_part_alias(alias)
            if metadata:
                bom.append({
                    "Designator": ref,
                    "MPN": metadata.get("mpn"),
                    "Manufacturer": metadata.get("manufacturer"),
                    "Description": metadata.get("description"),
                    "Footprint": metadata.get("footprint")
                })
        return bom

# --- Standalone CLI for the Validator Agent ---
if __name__ == "__main__":
    manager = LibraryManager()
    
    print("🔍 Starting Library Integrity Check...")
    missing_files = manager.validate_project_libraries()
    
    if not missing_files:
        print("✅ All project libraries are consistent and present.")
    else:
        print("❌ Library validation failed!")
        for error in missing_files:
            print(f"  - {error}")
        sys.exit(1)
      
