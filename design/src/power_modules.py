from skidl import *

def ldo_regulator_3v3(vin_net, gnd_net):
    """
    Standard Linear Regulator Module (AMS1117-3.3).
    Converts 5V input to a stable 3.3V output for MCU logic.
    """
    vout_net = Net('VCC_3V3')

    # Part(Library, Component, Footprint)
    # Using SOT-223 for better thermal dissipation in enterprise designs
    reg = Part('Regulator_Linear', 'AMS1117-3.3', footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2')
    
    # Input Filtering: 10uF Tantalum or Electrolytic
    c_in = Part('Device', 'C', value='10uF', footprint='Capacitor_SMD:C_0805_2012Metric')
    
    # Output Stability: 22uF Ceramic (Essential for AMS1117 stability)
    c_out = Part('Device', 'C', value='22uF', footprint='Capacitor_SMD:C_1206_3216Metric')

    # Logical Connections
    # reg['IN', 'OUT', 'GND'] notation for cleaner mapping
    reg['IN', 'GND'] += vin_net, gnd_net
    reg['OUT', 'GND'] += vout_net, gnd_net

    # Place capacitors in parallel with Input and Output rails
    c_in[1, 2] += vin_net, gnd_net
    c_out[1, 2] += vout_net, gnd_net

    print(f"  [Power Module] LDO 3.3V initialized on Net: {vout_net.name}")
    return vout_net

def buck_converter_generic(vin_net, gnd_net, target_v="5V"):
    """
    Placeholder for a High-Efficiency Switching Regulator.
    Used for high-current applications where LDO heat is a concern.
    """
    vout_net = Net(f'VCC_{target_v}')
    
    # In a real enterprise pod, this would include the Inductor, 
    # Schottky Diode, and Feedback resistor network logic.
    # Logic: R1 = R2 * (Vout/Vref - 1)
    
    print(f"  [Power Module] Buck Converter {target_v} initialized.")
    return vout_net

def power_indicator_led(vcc_net, gnd_net, color="Green"):
    """
    Simple status LED with current-limiting resistor.
    """
    led = Part('Device', 'LED', footprint='LED_SMD:LED_0805_2012Metric')
    res = Part('Device', 'R', value='1k', footprint='Resistor_SMD:R_0603_1608Metric')

    vcc_net += res[1]
    res[2] += led[1]
    led[2] += gnd_net
    
    return led
