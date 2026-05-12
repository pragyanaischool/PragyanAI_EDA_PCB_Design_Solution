import re
import os

class FootprintAnalyzer:
    """
    Parses .kicad_mod files to extract physical dimensions 
    and pad coordinates for AI placement logic.
    """
    def __init__(self, library_path):
        self.library_path = library_path

    def get_footprint_bounds(self, footprint_name):
        """
        Calculates the bounding box (width/height) of a footprint 
        based on its Courtyard (CrtYd) layer.
        """
        file_path = os.path.join(self.library_path, f"{footprint_name}.kicad_mod")
        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r') as f:
            data = f.read()

        # Find courtyard lines to determine physical size
        coords = re.findall(r'\(fp_line \(start (.*?) (.*?)\) \(end (.*?) (.*?)\) \(layer "F\.CrtYd"\)', data)
        
        if not coords:
            return {"width": 1.0, "height": 1.0} # Fallback

        x_pts = [float(c[0]) for c in coords] + [float(c[2]) for c in coords]
        y_pts = [float(c[1]) for c in coords] + [float(c[3]) for c in coords]
        
        return {
            "width": max(x_pts) - min(x_pts),
            "height": max(y_pts) - min(y_pts),
            "center_offset": (sum(x_pts)/len(x_pts), sum(y_pts)/len(y_pts))
        }

if __name__ == "__main__":
    analyzer = FootprintAnalyzer("design/lib/footprints/Pragyan_Standard.pretty")
    bounds = analyzer.get_footprint_bounds("R_0603_1608Metric")
    print(f"📏 Footprint Dimensions: {bounds}")
  
