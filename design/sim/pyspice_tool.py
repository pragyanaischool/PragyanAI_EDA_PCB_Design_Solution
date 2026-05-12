import os
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

class PySpiceSimulator:
    """
    Automated simulation engine for PragyanAI hardware verification.
    Supports Transient, AC, and Operating Point analysis.
    """
    def __init__(self, title="Hardware Simulation"):
        self.circuit = Circuit(title)
        self.model_dir = os.path.join(os.path.dirname(__file__), "models")

    def include_model(self, model_file):
        """Includes a manufacturer's .lib file into the simulation."""
        path = os.path.join(self.model_dir, model_file)
        if os.path.exists(path):
            self.circuit.include(path)
        else:
            print(f"⚠️ Warning: Model {model_file} not found.")

    def run_transient(self, step_ms=0.1, final_ms=10):
        """Runs a Transient Analysis (Time vs Voltage)."""
        simulator = self.circuit.simulator(temperature=25, nominal_temperature=25)
        analysis = simulator.transient(step_time=ms(step_ms), end_time=ms(final_ms))
        return analysis

    def check_voltage_rail(self, analysis, node_name, target_v, tolerance=0.05):
        """
        Validates if a voltage rail is within an acceptable range.
        Standard tolerance: 5%.
        """
        voltage = float(analysis[node_name][-1]) # Get steady-state value
        lower_bound = target_v * (1 - tolerance)
        upper_bound = target_v * (1 + tolerance)
        
        if lower_bound <= voltage <= upper_bound:
            return True, voltage
        return False, voltage

# Standard simulator instance
sim_engine = PySpiceSimulator()
