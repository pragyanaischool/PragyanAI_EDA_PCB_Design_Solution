import os
from pyspice_tool import sim_engine
from PySpice.Unit import *

def test_power_rail_stability():
    """
    Test Case: 5V to 3.3V Step Response.
    Simulates plugging in a USB cable and monitors the LDO output
    for overshoot, ringing, and steady-state accuracy.
    """
    circuit = sim_engine.circuit
    
    # 1. Define the Input Power Source
    # Simulates a fast 5V rise starting at 1ms
    # Pulse(v_initial, v_peak, delay, rise_time, fall_time, pulse_width)
    circuit.V('input', 'Vin', circuit.gnd, 'dc 0V pulse(0V 5V 1ms 10us)')
    
    # 2. Include Component Models
    # These point to manufacturer-provided SPICE models in design/sim/models/
    sim_engine.include_model("ams1117.lib")
    
    # 3. Define Circuit Topology (Abstracted Netlist)
    # Trace resistance (500 mOhms)
    circuit.R(1, 'Vin', 'Vreg_IN', 0.5@u_Ohm)
    
    # Instantiate the AMS1117 LDO
    # Pins: IN, OUT, ADJ/GND
    circuit.X('U1', 'AMS1117', 'Vreg_IN', 'Vout_3v3', circuit.gnd)
    
    # Output Filter (22uF Tantalum + 100nF Ceramic)
    circuit.C(1, 'Vout_3v3', circuit.gnd, 22@u_uF)
    circuit.C(2, 'Vout_3v3', circuit.gnd, 100@u_nF)
    
    # Simulate a variable load (e.g., an ESP32 waking up)
    # 33 Ohms = ~100mA current draw at 3.3V
    circuit.R('load', 'Vout_3v3', circuit.gnd, 33@u_Ohm)

    # 4. Execute Simulation
    print("🚀 Initializing Power Rail Simulation...")
    # Step = 10us, Total Time = 5ms
    analysis = sim_engine.run_transient(step_ms=0.01, final_ms=5)
    
    # 5. Automated Pass/Fail Checks
    steady_state_v = float(analysis['vout_3v3'][-1])
    peak_v = max(analysis['vout_3v3'])
    overshoot = ((peak_v - steady_state_v) / steady_state_v) * 100
    
    print("-" * 30)
    print(f"RESULT: Steady State: {steady_state_v:.3f}V")
    print(f"RESULT: Peak Voltage: {peak_v:.3f}V")
    print(f"RESULT: Overshoot: {overshoot:.2f}%")
    
    # Validation Logic
    success, current_v = sim_engine.check_voltage_rail(analysis, 'vout_3v3', 3.3)
    
    if success and overshoot < 5.0:
        print("✅ PASS: Power rail is stable and within 5% tolerance.")
    else:
        print("❌ FAIL: Power rail instability detected.")
        if overshoot >= 5.0:
            print("  - Danger: Overshoot exceeds safe limits for MCU.")

if __name__ == "__main__":
    test_power_rail_stability()
  
