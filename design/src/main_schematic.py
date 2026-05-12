from skidl import *

def generate_pcb_logic():
    # 1. Define Power Nets
    vcc = Net('VCC')
    gnd = Net('GND')

    # 2. Instantiate Components (Mappings provided by Component Agent)
    # Part(Library, Component_Name, Footprint)
    mcu = Part('MCU_Espressif_ESP32', 'ESP32-WROOM-32', footprint='RF_Module:ESP32-WROOM-32')
    ldo = Part('Regulator_Linear', 'AMS1117-3.3', footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2')
    cap = Part('Device', 'C', value='10uF', footprint='Capacitor_SMD:C_0805_2012Metric')

    # 3. Define Connections
    ldo['IN', 'GND'] += vcc, gnd
    ldo['OUT', 'GND'] += mcu['3V3'], gnd
    
    # Decoupling logic
    cap[1, 2] += ldo['OUT'], gnd

    print("✅ Schematic logic compiled successfully.")

if __name__ == "__main__":
    generate_pcb_logic()
    ERC()              # Run Electrical Rule Check
    generate_netlist() # Export for KiCad Layout
