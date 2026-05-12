from skidl import *

def esp32_wroom_32_core(vcc_3v3, gnd):
    """
    Minimal Core Circuit for ESP32-WROOM-32.
    Includes decoupling, Enable (EN) pull-up, and Boot (IO0) pull-up.
    """
    # 1. Instantiate the MCU
    mcu = Part('MCU_Espressif_ESP32', 'ESP32-WROOM-32', footprint='RF_Module:ESP32-WROOM-32')

    # 2. Power and Ground Connections
    # ESP32-WROOM pins: 3V3 is pin 2, GND is pin 1, 15, 38, 39
    mcu['3V3'] += vcc_3v3
    mcu['GND'] += gnd

    # 3. Decoupling Network (Critical for RF stability)
    # Recommended: 10uF + 100nF close to the VCC pin
    c_bulk = Part('Device', 'C', value='10uF', footprint='Capacitor_SMD:C_0805_2012Metric')
    c_filter = Part('Device', 'C', value='100nF', footprint='Capacitor_SMD:C_0603_1608Metric')
    
    c_bulk[1, 2] += vcc_3v3, gnd
    c_filter[1, 2] += vcc_3v3, gnd

    # 4. Control Signals (EN and IO0)
    # EN (Reset) needs a pull-up and a delay capacitor for clean startup
    r_en = Part('Device', 'R', value='10k', footprint='Resistor_SMD:R_0603_1608Metric')
    c_en = Part('Device', 'C', value='100nF', footprint='Capacitor_SMD:C_0603_1608Metric')
    
    r_en[1, 2] += vcc_3v3, mcu['EN']
    c_en[1, 2] += mcu['EN'], gnd

    # IO0 needs a pull-up to stay in 'Run' mode (Low = Bootloader mode)
    r_boot = Part('Device', 'R', value='10k', footprint='Resistor_SMD:R_0603_1608Metric')
    r_boot[1, 2] += vcc_3v3, mcu['IO0']

    print(f"  [MCU Core] ESP32-WROOM-32 infrastructure initialized.")
    return mcu

def stm32_f103_core(vcc_3v3, gnd):
    """
    Minimal Core Circuit for STM32F103 (Blue Pill style).
    Includes decoupling for all VDD pins and NRST pull-up.
    """
    mcu = Part('MCU_ST_STM32F1', 'STM32F103C8Tx', footprint='Package_QFP:LQFP-48_7x7mm_P0.5mm')
    
    # Decoupling for multiple VDD pins (usually 4-5 on LQFP-48)
    for i in range(1, 5):
        cap = Part('Device', 'C', value='100nF', footprint='Capacitor_SMD:C_0603_1608Metric')
        cap[1, 2] += vcc_3v3, gnd
    
    mcu['VDD'] += vcc_3v3
    mcu['VSS'] += gnd
    
    # Reset Logic
    nrst_pullup = Part('Device', 'R', value='10k', footprint='Resistor_SMD:R_0603_1608Metric')
    nrst_pullup[1, 2] += vcc_3v3, mcu['NRST']
    
    print(f"  [MCU Core] STM32F103 core initialized with distributed decoupling.")
    return mcu
  
