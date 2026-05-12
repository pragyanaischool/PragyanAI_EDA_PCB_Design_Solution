import json
from design.sim.pyspice_tool import sim_engine

class SI_PI_Agent:
    """
    Analysis Cluster: SI/PI Agent.
    Orchestrates SPICE simulations to ensure electrical stability.
    """
    def __init__(self, netlist_path="design/output/project.net"):
        self.netlist_path = netlist_path
        self.report_path = "design/output/si_pi_report.json"

    def validate_power_delivery(self, target_v=3.3):
        """
        Runs a transient analysis to check if the power rail stabilizes
        within the 5% tolerance defined in drc_rules.
        """
        print("⚡ SI/PI Agent: Initializing Power Integrity simulation...")
        
        # In a production environment, this agent would parse the 
        # actual netlist and convert it to a SPICE deck.
        # Here we invoke the standardized testbench.
        from design.sim.testbench import run_ldo_power_on_test
        
        # Capture simulation metrics
        metrics = run_ldo_power_on_test()
        
        # Decision Logic
        status = "PASS" if metrics['success'] else "FAIL"
        
        report = {
            "test_name": "Power_On_Stabilization",
            "target_voltage": target_v,
            "measured_voltage": metrics.get('steady_v'),
            "overshoot_percent": metrics.get('overshoot'),
            "status": status
        }
        
        return report

    def save_report(self, report):
        with open(self.report_path, 'w') as f:
            json.dump(report, f, indent=4)
        print(f"✅ SI/PI Agent: Electrical validation report saved.")

if __name__ == "__main__":
    agent = SI_PI_Agent()
    res = agent.validate_power_delivery()
    agent.save_report(res)
  
