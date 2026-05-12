import os
from typing import TypedDict, List, Dict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Import local pods (Assume these are defined in your agents/ directory)
from agents.planning.req_agent import requirement_analyst
from agents.planning.arch_agent import architecture_specialist
from agents.implementation.bom_agent import component_selector
from agents.implementation.skidl_agent import schematic_generator

# 1. Define the State Schema
class PCBDesignState(TypedDict):
    """
    The shared 'Memory' of the AI system. 
    Every agent reads from and writes to this state.
    """
    raw_input: str               # Original PRD or prompt
    project_specs: Dict          # Structured JSON from Req Agent
    block_diagram: str           # Mermaid/SVG code
    selected_components: List[Dict] # Validated BOM
    skidl_source_code: str       # Python code for schematic
    is_approved: bool            # Human approval flag
    feedback: str                # Human feedback for loops
    current_step: str            # Tracking progress

# 2. Node Wrapper Functions
def req_node(state: PCBDesignState):
    print("--- [Agent: Requirement Analyst] ---")
    result = requirement_analyst(state["raw_input"])
    return {"project_specs": result, "current_step": "Requirement Extraction Completed"}

def arch_node(state: PCBDesignState):
    print("--- [Agent: Architecture Specialist] ---")
    result = architecture_specialist(state["project_specs"])
    return {"block_diagram": result, "current_step": "Architecture Drafted"}

def bom_node(state: PCBDesignState):
    print("--- [Agent: Component Selector] ---")
    # This node uses RAG tool internally
    result = component_selector(state["block_diagram"])
    return {"selected_components": result, "current_step": "BOM Generated"}

def skidl_node(state: PCBDesignState):
    print("--- [Agent: Schematic Generator] ---")
    result = schematic_generator(state["selected_components"])
    return {"skidl_source_code": result, "current_step": "Schematic Python Code Generated"}

# 3. Logic for Human-in-the-Loop (Conditional Edges)
def should_continue(state: PCBDesignState):
    """
    Checks if the human has approved the current state.
    If not, it keeps the graph in an 'interrupt' state.
    """
    if state.get("is_approved", False):
        return "continue"
    return "ask_human"

# 4. Orchestrating the Graph
def create_pcb_orchestrator():
    # Initialize the State Machine
    builder = StateGraph(PCBDesignState)

    # Add Pod Nodes
    builder.add_node("planning_req", req_node)
    builder.add_node("planning_arch", arch_node)
    builder.add_node("implementation_bom", bom_node)
    builder.add_node("implementation_skidl", skidl_node)

    # Define the Linear Flow with Entry Point
    builder.set_entry_point("planning_req")
    builder.add_edge("planning_req", "planning_arch")
    builder.add_edge("planning_arch", "implementation_bom")
    builder.add_edge("implementation_bom", "implementation_skidl")
    builder.add_edge("implementation_skidl", END)

    # Setup Memory for HITL Persistence
    # This allows you to 'pause' the graph and resume later from the same state
    memory = MemorySaver()

    # Compile the Graph with Interrupts
    # Interrupt after planning and BOM selection to ensure human review
    graph = builder.compile(
        checkpointer=memory,
        interrupt_after=["planning_arch", "implementation_bom"]
    )
    
    return graph

# Example of how to initialize the graph in main_app.py
# pcb_ai = create_pcb_orchestrator()
# config = {"configurable": {"thread_id": "project_001"}}
# pcb_ai.invoke({"raw_input": "4-layer ESP32 board"}, config)
