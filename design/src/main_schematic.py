from skidl import *

# 1. Define the core circuit function
def create_enterprise_pcb():
    """
    Main hardware logic defined as code.
    This replaces the graphical schematic entry.
    """
    # Initialize the Global Power Nets
    vcc_5v = Net('VCC_5V')    # Input Power
    vcc_3v3 = Net('VCC_3V3')  # Regulated Power
    gnd = Net('GND')          # Ground Plane

    # ---------------------------------------------------------
    # 2. POWER STAGE (LDO Regulator)
    # ---------------------------------------------------------
    # Mapping MPN to Footprint via the SKiDL Part object
    # Part(Library, Component, Footprint)
    regulator = Part('Regulator_Linear', 'AMS1117-3.3', footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2')
    
    # Input/Output Decoupling Capacitors
    c_in = Part('Device', 'C', value='10uF', footprint='Capacitor_SMD:C_0805_2012Metric')
    c_out = Part('Device', 'C', value='22uF', footprint='Capacitor_SMD:C_1206_3216Metric')

    # Connections for the Power Stage
    regulator['IN', 'GND'] += vcc_5v, gnd
    regulator['OUT', 'GND'] += vcc_3v3, gnd
    
    # Parallel capacitors for filtering
    c_in[1, 2] += vcc_5v, gnd
    c_out[1, 2] += vcc_3v3, gnd

    # ---------------------------------------------------------
    # 3. CONTROLLER STAGE (ESP32)
    # ---------------------------------------------------------
    mcu = Part('MCU_Espressif_ESP32', 'ESP32-WROOM-32', footprint='RF_Module:ESP32-WROOM-32')

    # Connect Power and Reset
    mcu['3V3', 'GND'] += vcc_3v3, gnd
    mcu['EN'] += vcc_3v3  # Standard pull-up for Enable

    # ---------------------------------------------------------
    # 4. INTERFACE STAGE (Status LED)
    # ---------------------------------------------------------
    led = Part('Device', 'LED', footprint='LED_SMD:LED_0805_2012Metric')
    r_limit = Part('Device', 'R', value='330', footprint='Resistor_SMD:R_0805_2012Metric')

    # Connect LED to a GPIO (e.g., IO2)
    mcu['IO2'] += r_limit[1]
    r_limit[2] += led[1]
    led[2] += gnd

    print("✅ Schematic Logic Compiled Successfully.")

# ---------------------------------------------------------
# 5. EXECUTION & EXPORT
# ---------------------------------------------------------
if __name__ == "__main__":
    # Reset any previous circuit state
    default_circuit.reset()
    
    # Run the generator
    create_enterprise_pcb()

    # Trigger Automated ERC (Electrical Rule Check)
    # This identifies floating pins or shorts before layout
    print("🚀 Running Electrical Rule Check...")
    ERC()

    # Generate the Netlist for the Physical Layout (KiCad Format)
    netlist_file = 'design/build/main_netlist.net'
    generate_netlist(file_ = netlist_file)
    print(f"📦 Netlist exported to {netlist_file}")
    
