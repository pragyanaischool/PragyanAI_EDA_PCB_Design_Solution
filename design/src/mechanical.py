from skidl import *

def add_mounting_holes(gnd_net=None, hole_size='M3', count=4):
    """
    Adds M3 (3.2mm) mounting holes to the PCB corners.
    If a gnd_net is provided, the holes will be plated and connected to Ground 
    to provide an EMI path to the chassis.
    """
    # M3_Pad_Via is the industry standard for grounded mounting
    footprint_name = 'MountingHole:MountingHole_3.2mm_M3_Pad_Via' if gnd_net else 'MountingHole:MountingHole_3.2mm_M3'
    
    for i in range(count):
        hole = Part('Mechanical', 'MountingHole_Pad', footprint=footprint_name)
        if gnd_net:
            hole[1] += gnd_net
            
    print(f"  [Mechanical] {count} {hole_size} mounting holes added (Grounded: {bool(gnd_net)}).")

def add_global_fiducials(count=3):
    """
    Adds Fiducial marks to the board.
    These are copper 'targets' that SMT pick-and-place machines use 
    to align the board with sub-millimeter precision.
    """
    # Standard 1mm copper / 2mm mask opening fiducial
    for i in range(count):
        Part('Mechanical', 'Fiducial', footprint='Fiducial:Fiducial_1mm_Mask2mm')
        
    print(f"  [Mechanical] {count} global fiducials added for SMT alignment.")

def add_logo_and_graphics():
    """
    Adds technical graphics and branding to the Silkscreen layer.
    """
    # Open Source Hardware Logo or Company Logo
    Part('Graphic', 'OSHW_Logo_Silkscreen_CopperTop_6mm', footprint='Symbol:OSHW-Logo_6mm_Silkscreen')
    
    # Static 'Danger High Voltage' or 'ESD Sensitive' warnings
    Part('Graphic', 'ESD_Warning_Small', footprint='Symbol:ESD-Logo_6mm_Silkscreen')
    
    print("  [Mechanical] Silkscreen logos and warnings added.")

def add_heatsink_area(thermal_net):
    """
    Defines a zone for a physical heatsink if the BOM Agent 
    identifies a high-heat component (like a motor driver).
    """
    # This usually maps to a copper zone or a specific heatsink part
    # that requires physical clearance in the layout.
    heatsink = Part('Mechanical', 'Heatsink_30x30mm', footprint='Heatsink:Heatsink_Stonecold_30x30mm')
    
    # Some heatsinks are soldered to GND for thermal conductivity
    if thermal_net:
        heatsink[1] += thermal_net
        
    print("  [Mechanical] Heatsink footprint reserved in layout.")
  
