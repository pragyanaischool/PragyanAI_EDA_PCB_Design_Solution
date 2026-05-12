import json
import os
from skidl import *

class SKiDLAgent:
    """
    The Implementation Cluster: SKiDL Agent.
    Converts the Architecture Plan into a Python-based schematic (SKiDL).
    """

    def __init__(self, plan_path: str = "design/config/architecture_plan.json"):
        self.plan_path = plan_path
        self.mapping_path = "design/lib/mapping.json"
        
        # Load constraints
        with open(self.plan_path, 'r') as f:
            self.plan = json.load(f)
        with open(self.mapping_path, 'r') as f:
            self.mapping = json.load(f)

    def _get_part(self, alias: str):
        """Helper to instantiate a part using mapping data."""
        part_data = self.mapping.get(alias)
        if not part_data:
            raise ValueError(f"Alias {alias} not found in library mapping.")
        
        # Create SKiDL Part
        # Assumes the symbol library is already in the sym_lib_table
        return Part(part_data['symbol'].split(':')[0], 
                    part_data['symbol'].split(':')[1], 
                    footprint=part_data['footprint'])

    def construct_circuit(self):
        """
        Translates the Architecture Plan into electrical connections.
        """
        print("🔌 SKiDLAgent: Constructing schematic logic...")
        
        # 1. Define Global Nets
        v_in = Net('V_IN')
        v_logic = Net('+3.3V')
        gnd = Net('GND')

        # 2. Power Section Logic
        for stage in self.plan['power_tree']:
            if stage['stage'] == "Regulation":
                reg = self._get_part(stage['part_alias'])
                
                # Standard LDO/Buck Wiring (In, Out, GND)
                # Note: Actual pin names come from symbol_extractor.py logic
                reg['IN'] += v_in
                reg['OUT'] += v_logic
                reg['GND'] += gnd
                
                # Automated decoupling capacitors
                c_in = Part('Device', 'C', value='10uF', footprint='Capacitor_SMD:C_0603_1608Metric')
                c_out = Part('Device', 'C', value='22uF', footprint='Capacitor_SMD:C_0805_2012Metric')
                
                c_in[1, 2] += v_in, gnd
                c_out[1, 2] += v_logic, gnd

        # 3. MCU Core Logic
        mcu_alias = "esp32_wroom_32e" # Pulled from spec in production
        mcu = self._get_part(mcu_alias)
        
        mcu['VDD', 'VDDA'] += v_logic
        mcu['GND'] += gnd

        # 4. Bus Implementation (I2C Example)
        if "I2C" in self.plan['bus_mapping']:
            i2c_cfg = self.plan['bus_mapping']['I2C']
            sda_net = Net('I2C_SDA')
            scl_net = Net('I2C_SCL')
            
            mcu[i2c_cfg['SDA']] += sda_net
            mcu[i2c_cfg['SCL']] += scl_net
            
            # Auto-add I2C Pull-ups
            r_sda = Part('Device', 'R', value='4.7k', footprint='Resistor_SMD:R_0603_1608Metric')
            r_scl = Part('Device', 'R', value='4.7k', footprint='Resistor_SMD:R_0603_1608Metric')
            
            r_sda[1, 2] += v_logic, sda_net
            r_scl[1, 2] += v_logic, scl_net

        print("✅ SKiDLAgent: Schematic construction complete.")

    def generate_netlist(self, output_path="design/output/project.net"):
        """Compiles the SKiDL code into a KiCad-readable netlist."""
        generate_netlist(file_ = output_path)
        print(f"📄 SKiDLAgent: Netlist generated at {output_path}")

if __name__ == "__main__":
    # Ensure a plan exists before running
    if os.path.exists("design/config/architecture_plan.json"):
        agent = SKiDLAgent()
        agent.construct_circuit()
        # agent.generate_netlist()
    else:
        print("❌ Error: No Architecture Plan found. Run ArchAgent first.")
      
