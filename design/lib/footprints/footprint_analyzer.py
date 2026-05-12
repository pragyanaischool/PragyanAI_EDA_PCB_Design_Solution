import os
import re
from typing import Dict, Tuple

class FootprintAnalyzer:
    """
    Library Logic: Footprint Analyzer.
    Parses KiCad footprint files (.kicad_mod) to extract physical 
    dimensions for collision-free placement.
    """

    def __init__(self, lib_path: str = "design/lib/footprints"):
        self.lib_path = lib_path

    def get_dimensions(self, footprint_name: str) -> Dict[str, float]:
        """
        Parses a .kicad_mod file to find the bounding box of the footprint.
        Returns width and height in mm.
        """
        # Format: LibraryName:FootprintName -> LibraryName.pretty/FootprintName.kicad_mod
        try:
            lib, name = footprint_name.split(':')
            file_path = os.path.join(self.lib_path, f"{lib}.pretty", f"{name}.kicad_mod")
        except ValueError:
            print(f"⚠️ Invalid footprint format: {footprint_name}")
            return {"width": 5.0, "height": 5.0} # Default safe fallback

        if not os.path.exists(file_path):
            print(f"⚠️ Footprint file not found: {file_path}")
            return {"width": 10.0, "height": 10.0}

        return self._parse_mod_file(file_path)

    def _parse_mod_file(self, file_path: str) -> Dict[str, float]:
        """
        Reads the S-expression format of KiCad and extracts 
        min/max X and Y coordinates of pads and courtyard lines.
        """
        x_coords = []
        y_coords = []

        with open(file_path, 'r') as f:
            content = f.read()

            # Regex to find pad positions: (at 1.27 -2.54)
            pad_matches = re.findall(r'\(at ([-+]?\d*\.\d+|\d+) ([-+]?\d*\.\d+|\d+)', content)
            for x, y in pad_matches:
                x_coords.append(float(x))
                y_coords.append(float(y))

            # Regex to find graphic lines (courtyard): (fp_line (start -2 -2) (end 2 -2) ...)
            line_matches = re.findall(r'\(start ([-+]?\d*\.\d+|\d+) ([-+]?\d*\.\d+|\d+)\)', content)
            for x, y in line_matches:
                x_coords.append(float(x))
                y_coords.append(float(y))

        if not x_coords or not y_coords:
            return {"width": 2.0, "height": 2.0}

        # Calculate Bounding Box
        width = max(x_coords) - min(x_coords)
        height = max(y_coords) - min(y_coords)

        # Add a 0.5mm "Courtyard" buffer for assembly clearance
        return {
            "width": round(width + 0.5, 2),
            "height": round(height + 0.5, 2),
            "area_mm2": round(width * height, 2)
        }

# --- Standalone Testing ---
if __name__ == "__main__":
    analyzer = FootprintAnalyzer()
    # Example: Analyzing a standard 0603 Capacitor
    dims = analyzer.get_dimensions("Capacitor_SMD:C_0603_1608Metric")
    print(f"📏 Analyzed Dimensions: {dims['width']}mm x {dims['height']}mm")
    
