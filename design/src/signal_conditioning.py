from skidl import *

def low_pass_filter(input_net, output_net, gnd_net, cutoff_freq_hz=1600):
    """
    Standard Passive RC Low-Pass Filter.
    Prevents high-frequency noise from aliasing in the ADC.
    Default: 1k Ohm + 100nF (~1.6kHz cutoff).
    """
    # Instantiate Parts
    res = Part('Device', 'R', value='1k', footprint='Resistor_SMD:R_0603_1608Metric')
    cap = Part('Device', 'C', value='100nF', footprint='Capacitor_SMD:C_0603_1608Metric')

    # Connectivity
    input_net += res[1]
    res[2] += output_net, cap[1]
    cap[2] += gnd_net

    print(f"  [Signal] Added RC Low-Pass Filter (Fc ~ {cutoff_freq_hz}Hz) to {output_net.name}")
    return output_net

def voltage_divider(input_net, output_net, gnd_net, r_top_val='10k', r_bottom_val='10k'):
    """
    Precision Voltage Divider.
    Used for scaling high voltage signals (e.g., Battery sensing) 
    to MCU-safe levels (e.g., 3.3V).
    """
    r_top = Part('Device', 'R', value=r_top_val, footprint='Resistor_SMD:R_0603_1608Metric')
    r_bottom = Part('Device', 'R', value=r_bottom_val, footprint='Resistor_SMD:R_0603_1608Metric')

    input_net += r_top[1]
    r_top[2] += output_net, r_bottom[1]
    r_bottom[2] += gnd_net

    print(f"  [Signal] Voltage Divider ({r_top_val}/{r_bottom_val}) scaled {input_net.name} to {output_net.name}")

def opamp_buffer(vin_net, vout_net, vcc_net, gnd_net):
    """
    Unity Gain Buffer (Voltage Follower).
    Used to provide high input impedance and low output impedance.
    Prevents 'Loading Effect' on sensitive sensors.
    """
    # Using a standard LM358 (Dual Op-Amp) for general purpose tasks
    op = Part('Amplifier_Operational', 'LM358', footprint='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm')

    # Power the Op-Amp
    op['V+', 'V-'] += vcc_net, gnd_net

    # Unity Gain Configuration: Output tied back to Inverting Input (-)
    op['+'] += vin_net
    op['-'] += op['OUT']
    op['OUT'] += vout_net

    print(f"  [Signal] Unity Gain Buffer added for {vin_net.name}")
    return vout_net

def sensor_protection_clamping(signal_net, vcc_net, gnd_net):
    """
    Schottky Diode Clamping.
    Protects ADC pins from overvoltage (>VCC) or undervoltage (<GND).
    """
    diode_pair = Part('Diode', 'BAT54S', footprint='Package_TO_SOT_SMD:SOT-23')

    # BAT54S consists of two Schottky diodes in series
    # Pin 1 to GND, Pin 2 to VCC, Pin 3 to Signal (Node between diodes)
    diode_pair[1] += gnd_net
    diode_pair[2] += vcc_net
    diode_pair[3] += signal_net

    print(f"  [Signal] Overvoltage Clamping added to {signal_net.name}")
  
