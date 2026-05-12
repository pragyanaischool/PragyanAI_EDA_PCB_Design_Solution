import os
import shutil
import zipfile
from datetime import datetime
from design.kicad_tool import kicad_tool

class FabAgent:
    """
    Fulfillment Cluster: Fabrication Agent.
    Finalizes the design by gathering all manufacturing deliverables 
    into a structured, versioned ZIP archive.
    """

    def __init__(self, project_name: str = "PragyanAI_Module"):
        self.project_name = project_name
        self.output_root = "design/output"
        self.fab_dir = os.path.join(self.output_root, "fab_files")
        
        # Define the target sub-directories for the factory
        self.folders = ["gerbers", "drill", "pnp", "bom"]

    def _cleanup_old_builds(self):
        """Ensures a fresh start for the current fabrication run."""
        if os.path.exists(self.fab_dir):
            shutil.rmtree(self.fab_dir)
        os.makedirs(self.fab_dir)
        for folder in self.folders:
            os.makedirs(os.path.join(self.fab_dir, folder))

    def prepare_factory_package(self) -> str:
        """
        Orchestrates the movement of files from various output 
        folders into a single zipped fabrication pack.
        """
        print(f"🏭 FabAgent: Starting production packaging for {self.project_name}...")
        
        self._cleanup_old_builds()

        # 1. Trigger KiCad Tool to generate the latest raw files
        # This calls the kicad-cli under the hood
        kicad_tool.generate_gerbers()

        # 2. Organize Files (Simulated file move logic)
        # In a production environment, this script copies the .gbr, .drl, 
        # and .pos files into the structured folders created above.
        print("📂 FabAgent: Organizing Gerbers, Drills, and PnP data...")

        # 3. Create Versioned Archive
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        zip_filename = f"{self.project_name}_FAB_RevA_{timestamp}.zip"
        zip_path = os.path.join(self.output_root, zip_filename)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as fab_zip:
            for root, dirs, files in os.walk(self.fab_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Create a flat structure inside the ZIP for easier factory ingestion
                    fab_zip.write(file_path, arcname=file)

        print(f"✅ FabAgent: Manufacturing pack created successfully.")
        print(f"📦 Final Archive: {zip_path}")
        
        return zip_path

    def notify_procurement(self, zip_path: str):
        """
        In an automated venture studio, this would trigger an API call 
        to a PCB manufacturer or an internal Slack notification.
        """
        filesize_kb = os.path.getsize(zip_path) / 1024
        print(f"🔔 Notification: {self.project_name} is ready for order ({filesize_kb:.2f} KB).")

# --- Standalone Fulfillment Workflow ---
if __name__ == "__main__":
    agent = FabAgent("Enterprise_V3")
    
    # 1. Check if design/output exists
    if not os.path.exists("design/output"):
        os.makedirs("design/output")
        
    # 2. Run the packaging process
    try:
        final_pack = agent.prepare_factory_package()
        agent.notify_procurement(final_pack)
    except Exception as e:
        print(f"❌ FabAgent Error: Packaging failed - {e}")
      
