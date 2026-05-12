import json
import os
from datetime import datetime

class DRCAgent:
    """
    Analysis Cluster: DRC Agent.
    Validates physical board metrics against factory constraints.
    Prevents manufacturing failures before file generation.
    """

    def __init__(self, rules_path: str = "design/config/drc_rules.json"):
        self.rules_path = rules_path
        self.report_path = "design/output/drc_report.json"
        
        if not os.path.exists(self.rules_path):
            raise FileNotFoundError(f"DRC Rules missing at {self.rules_path}")
            
        with open(self.rules_path, 'r') as f:
            self.rules = json.load(f)

    def run_validation(self, layout_stats: dict) -> dict:
        """
        Compares actual layout data (provided by the Layout engine) 
        against the JSON ruleset.
        """
        print("🔍 DRCAgent: Executing Design Rule Check...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "PASS",
            "violations": [],
            "metrics_checked": 0
        }

        # 1. Trace Width Validation
        results["metrics_checked"] += 1
        min_w = self.rules['constraints']['min_trace_width']
        if layout_stats['min_trace_width'] < min_w:
            results["violations"].append({
                "type": "TRACE_WIDTH",
                "error": f"Found width {layout_stats['min_trace_width']}mm. Factory min is {min_w}mm.",
                "severity": "CRITICAL"
            })

        # 2. Clearance (Space) Validation
        results["metrics_checked"] += 1
        min_c = self.rules['constraints']['min_clearance']
        if layout_stats['min_clearance'] < min_c:
            results["violations"].append({
                "type": "CLEARANCE",
                "error": f"Found spacing {layout_stats['min_clearance']}mm. Factory min is {min_c}mm.",
                "severity": "CRITICAL"
            })

        # 3. Via Drill Size Validation
        results["metrics_checked"] += 1
        min_d = self.rules['constraints']['min_via_drill']
        if layout_stats['min_via_drill'] < min_d:
            results["violations"].append({
                "type": "DRILL_SIZE",
                "error": f"Found drill {layout_stats['min_via_drill']}mm. Factory min is {min_d}mm.",
                "severity": "CRITICAL"
            })

        # Final Status Update
        if any(v['severity'] == "CRITICAL" for v in results["violations"]):
            results["overall_status"] = "FAIL"

        self._save_report(results)
        return results

    def _save_report(self, report_data: dict):
        os.makedirs(os.path.dirname(self.report_path), exist_ok=True)
        with open(self.report_path, 'w') as f:
            json.dump(report_data, f, indent=4)
        print(f"✅ DRCAgent: Validation complete. Status: {report_data['overall_status']}")

# --- Standalone Execution Logic ---
if __name__ == "__main__":
    # Simulated data derived from the Layout Agent/KiCad Backend
    board_metrics = {
        "min_trace_width": 0.12, # Violation (Rules say 0.1524)
        "min_clearance": 0.20,   # Safe
        "min_via_drill": 0.3,    # Safe
        "total_nets": 14,
        "unrouted_nets": 0
    }
    
    try:
        checker = DRCAgent()
        report = checker.run_validation(board_metrics)
        
        if report["overall_status"] == "FAIL":
            print(f"❌ DRC FAILED: {len(report['violations'])} violations found.")
            for v in report["violations"]:
                print(f"   - [{v['type']}] {v['error']}")
        else:
            print("🎉 DRC PASSED: Design is manufacture-ready.")
            
    except Exception as e:
        print(f"⚠️ DRC Agent Error: {e}")
      
