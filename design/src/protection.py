from skidl import *

def usb_esd_protection(usb_dp, usb_dn, vcc_5v, gnd):
    """
    High-Speed ESD Protection for USB 2.0 Data Lines.
    Uses a TVS diode array (e.g., USBLC6-2SC6) to steer transients to GND.
    """
    # USBLC6-2 is a industry standard for low-capacitance ESD protection
    tvs = Part('Power_Protection', 'USBLC6-2SC6', footprint='Package_TO_SOT_SMD:SOT-23-6')
    
    # Logic: Pin 1 & 3 are IO (Data), Pin 2 is GND, Pin 5 is VCC
    tvs[1] += usb_dp
    tvs[3] += usb_dn
    tvs[2] += gnd
    tvs[5] += vcc_5v
    
    # Internal protection pins 4 & 6 are usually mirrors of 1 & 3 for pass-through
    tvs[4] += usb_dp
    tvs[6] += usb_dn

    print("  [Protection] USBLC6 High-speed ESD protection added to USB data.")
    return tvs

def reverse_polarity_schottky(vin_raw, vin_protected):
    """
    Simple Reverse Polarity Protection using a Schottky Diode.
    Prevents circuit destruction if VCC and GND are swapped at the input.
    Note: Causes a ~0.3V - 0.4V drop.
    """
    # SMA package is robust for 1A - 3A inputs
    d = Part('Device', 'D_Schottky', footprint='Diode_SMD:D_SMA')
    
    d[1, 2] += vin_raw, vin_protected
    
    print(f"  [Protection] Schottky Reverse Polarity protection added ({vin_raw.name} -> {vin_protected.name})")
    return d

def battery_protection_p_mosfet(vin_raw, vin_protected, gnd):
    """
    High-Efficiency Reverse Polarity Protection using a P-Channel MOSFET.
    Ideal for battery-powered devices to avoid the voltage drop of a diode.
    """
    mos = Part('Device', 'Q_PMOS_GSD', footprint='Package_TO_SOT_SMD:SOT-23')
    
    # Connections for P-MOSFET protection:
    # Source to Raw Input, Drain to Protected Output, Gate to Ground
    mos['S'] += vin_raw
    mos['D'] += vin_protected
    mos['G'] += gnd
    
    print("  [Protection] High-efficiency P-MOSFET reverse polarity protection added.")
    return mos

def tvs_surge_clamping(power_net, gnd_net, voltage_peak=5.0):
    """
    Transient Voltage Suppressor (TVS) Diode for Power Rail Clamping.
    Protects against surges and 'load dump' spikes.
    """
    # SMAJ series is common for power rail clamping
    tvs = Part('Device', 'D_TVS', footprint='Diode_SMD:D_SMA')
    
    # TVS is placed in parallel: Anode to GND, Cathode to Power
    tvs[1, 2] += gnd_net, power_net
    
    print(f"  [Protection] TVS Clamping ({voltage_peak}V) added to {power_net.name}")
  
