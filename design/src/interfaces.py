from skidl import *

def usb_c_power_5v(vcc_5v, gnd):
    """
    USB-C Receptacle configured as a Power Sink (UFP).
    Includes 5.1k Ohm pulldowns on CC1/CC2 to request 5V from a PD source.
    """
    # Instantiate USB-C Connector (16-pin or 24-pin variants)
    usb = Part('Connector', 'USB_C_Receptacle_USB2.0', footprint='Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12')
    
    # CC configuration resistors (Required for USB-C to provide power)
    r_cc1 = Part('Device', 'R', value='5.1k', footprint='Resistor_SMD:R_0603_1608Metric')
    r_cc2 = Part('Device', 'R', value='5.1k', footprint='Resistor_SMD:R_0603_1608Metric')

    # Connections
    usb['VBUS'] += vcc_5v
    usb['GND'] += gnd
    
    # Pull CC pins to ground to signal 'Power Sink' mode to the host
    usb['CC1'] += r_cc1[1]; r_cc1[2] += gnd
    usb['CC2'] += r_cc2[1]; r_cc2[2] += gnd
    
    # Shield grounding
    usb['SHIELD'] += gnd

    print("  [Interface] USB-C 5V Power Sink initialized.")
    return usb

def uart_debug_header(tx_net, rx_net, gnd_net):
    """
    Standard 0.1" (2.54mm) pitch UART header for serial debugging.
    Order: TX, RX, GND
    """
    header = Part('Connector', 'Conn_01x03_Pin', footprint='Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical')
    
    header[1] += tx_net
    header[2] += rx_net
    header[3] += gnd_net
    
    print("  [Interface] UART Debug Header (3-pin) added.")
    return header

def i2c_bus_with_pullups(sda_net, scl_net, vcc_net):
    """
    Adds required pull-up resistors to an I2C bus.
    Essential for open-drain communication.
    """
    r_sda = Part('Device', 'R', value='4.7k', footprint='Resistor_SMD:R_0603_1608Metric')
    r_scl = Part('Device', 'R', value='4.7k', footprint='Resistor_SMD:R_0603_1608Metric')
    
    r_sda[1, 2] += vcc_net, sda_net
    r_scl[1, 2] += vcc_net, scl_net
    
    print("  [Interface] I2C Pull-ups (4.7k) added to bus.")

def swd_programming_header(swdio, swclk, reset, vcc, gnd):
    """
    Standard 5-pin SWD header for STM32/Cortex-M programming.
    """
    header = Part('Connector', 'Conn_01x05_Pin', footprint='Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical')
    
    header[1] += vcc
    header[2] += swclk
    header[3] += gnd
    header[4] += swdio
    header[5] += reset
    
    print("  [Interface] SWD Programming Header (5-pin) added.")
    return header
  
