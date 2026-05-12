from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ComponentModel(BaseModel):
    """Schema for a single electronic component validated by the BOM Agent."""
    designator: str = Field(..., description="Reference designator, e.g., U1, R1, C10")
    mpn: str = Field(..., description="Manufacturer Part Number")
    manufacturer: str
    description: str
    footprint: str = Field(..., description="KiCad footprint name")
    library_ref: str = Field(..., description="Symbol library reference")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Voltage, tolerance, etc.")
    status: str = "selected" # selected, verified, eol, substitute

class RequirementSpec(BaseModel):
    """Structured requirements extracted from the PRD."""
    mcu_family: Optional[str] = None
    input_voltage: str = "5V"
    interfaces: List[str] = [] # USB, SPI, I2C, etc.
    pcb_layers: int = 2
    dimensions_mm: Dict[str, float] = {"width": 0.0, "height": 0.0}
    constraints: List[str] = []

class DesignArtifacts(BaseModel):
    """Paths or raw data for generated files."""
    skidl_source_path: Optional[str] = None
    netlist_path: Optional[str] = None
    pcb_file_path: Optional[str] = None
    gerber_zip_path: Optional[str] = None

class PCBDesignState(BaseModel):
    """
    The Master State object for the LangGraph Orchestrator.
    This tracks the entire lifecycle of the PCB project.
    """
    # Project Metadata
    project_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    # 1. Planning Phase
    raw_input_text: str
    structured_requirements: RequirementSpec = Field(default_factory=RequirementSpec)
    block_diagram_mermaid: str = ""
    
    # 2. Implementation Phase
    bom: List[ComponentModel] = Field(default_factory=list)
    skidl_code: str = ""
    
    # 3. Analysis & Verification Phase
    erc_results: Dict[str, Any] = Field(default_factory=dict)
    drc_errors: List[str] = Field(default_factory=list)
    simulation_logs: str = ""
    
    # 4. State Control & HITL (Human-In-The-Loop)
    current_agent: str = "requirement_analyst"
    is_approved: bool = False
    revision_count: int = 0
    human_feedback: str = ""
    
    # 5. Output Data
    artifacts: DesignArtifacts = Field(default_factory=DesignArtifacts)

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
      
