import os
import re
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import streamlit as st

# --- Safe Fallback Import for Orchestrator ---
try:
    from orchestrator import PragyanOrchestrator
except ImportError:
    class PragyanOrchestrator:
        pass


# ==============================================================================
# Pure-Python KiCad PCB S-Expression Parser (Zero C/C++ Extensions)
# ==============================================================================

_TOKEN_RE = re.compile(r'[()]|"(?:\\.|[^"\\])*"|[^\s()]+')


def parse_sexpr(text: str) -> List[Any]:
    """Parses S-expression string into nested Python lists."""
    tokens = _TOKEN_RE.findall(text)
    if not tokens:
        return []

    stack: List[List[Any]] = [[]]
    for token in tokens:
        if token == "(":
            new_list: List[Any] = []
            stack[-1].append(new_list)
            stack.append(new_list)
        elif token == ")":
            if len(stack) > 1:
                stack.pop()
        else:
            if token.startswith('"') and token.endswith('"'):
                val: Union[str, int, float] = token[1:-1].encode("utf-8").decode("unicode_escape")
            else:
                try:
                    val = int(token)
                except ValueError:
                    try:
                        val = float(token)
                    except ValueError:
                        val = token
            stack[-1].append(val)

    return stack[0][0] if stack[0] else []


@dataclass
class Pad:
    number: str
    pad_type: str
    shape: str
    x: float
    y: float
    rotation: float
    size: Tuple[float, float]
    layers: List[str]
    net_code: Optional[int] = None
    net_name: Optional[str] = None


@dataclass
class Footprint:
    reference: str
    value: str
    footprint_name: str
    layer: str
    x: float
    y: float
    rotation: float
    pads: List[Pad] = field(default_factory=list)


@dataclass
class TrackSegment:
    start: Tuple[float, float]
    end: Tuple[float, float]
    width: float
    layer: str
    net_code: int


@dataclass
class Via:
    at: Tuple[float, float]
    size: float
    drill: float
    layers: Tuple[str, str]
    net_code: int


@dataclass
class ParsedPCB:
    version: Optional[int] = None
    generator: Optional[str] = None
    nets: Dict[int, str] = field(default_factory=dict)
    footprints: List[Footprint] = field(default_factory=list)
    tracks: List[TrackSegment] = field(default_factory=list)
    vias: List[Via] = field(default_factory=list)


class KiCadPCBParser:
    """Parses .kicad_pcb files into structured Python objects."""

    def __init__(self, filepath_or_text: Union[str, Path], is_raw_text: bool = False):
        self.is_raw_text = is_raw_text
        self.source = filepath_or_text
        self.raw_ast: List[Any] = []
        self.pcb: Optional[ParsedPCB] = None

    def parse(self) -> ParsedPCB:
        if self.is_raw_text:
            content = str(self.source)
        else:
            with open(self.source, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

        self.raw_ast = parse_sexpr(content)
        if not self.raw_ast or self.raw_ast[0] != "kicad_pcb":
            raise ValueError("Invalid KiCad PCB format. Root token must be 'kicad_pcb'.")

        pcb = ParsedPCB()

        for node in self.raw_ast[1:]:
            if not isinstance(node, list) or not node:
                continue

            tag = node[0]
            if tag == "version":
                pcb.version = node[1]
            elif tag == "generator":
                pcb.generator = str(node[1])
            elif tag == "net":
                pcb.nets[node[1]] = str(node[2]) if len(node) > 2 else ""
            elif tag in ("footprint", "module"):
                pcb.footprints.append(self._parse_footprint(node))
            elif tag == "segment":
                pcb.tracks.append(self._parse_segment(node))
            elif tag == "via":
                pcb.vias.append(self._parse_via(node))

        self.pcb = pcb
        return pcb

    def _parse_footprint(self, node: List[Any]) -> Footprint:
        footprint_name = node[1] if len(node) > 1 and isinstance(node[1], str) else ""
        layer = "F.Cu"
        x, y, rot = 0.0, 0.0, 0.0
        reference = ""
        value = ""
        pads: List[Pad] = []

        for item in node[1:]:
            if not isinstance(item, list) or not item:
                continue

            sub_tag = item[0]
            if sub_tag == "layer":
                layer = str(item[1])
            elif sub_tag == "at":
                x = float(item[1])
                y = float(item[2])
                rot = float(item[3]) if len(item) > 3 else 0.0
            elif sub_tag in ("fp_text", "property"):
                text_type = str(item[1])
                text_val = str(item[2]) if len(item) > 2 else ""
                if text_type.lower() == "reference":
                    reference = text_val
                elif text_type.lower() == "value":
                    value = text_val
            elif sub_tag == "pad":
                pads.append(self._parse_pad(item))

        return Footprint(
            reference=reference,
            value=value,
            footprint_name=footprint_name,
            layer=layer,
            x=x,
            y=y,
            rotation=rot,
            pads=pads,
        )

    def _parse_pad(self, node: List[Any]) -> Pad:
        number = str(node[1]) if len(node) > 1 else ""
        pad_type = str(node[2]) if len(node) > 2 else ""
        shape = str(node[3]) if len(node) > 3 else ""

        px, py, prot = 0.0, 0.0, 0.0
        sx, sy = 0.0, 0.0
        layers: List[str] = []
        net_code: Optional[int] = None
        net_name: Optional[str] = None

        for item in node[4:]:
            if not isinstance(item, list) or not item:
                continue

            tag = item[0]
            if tag == "at":
                px = float(item[1])
                py = float(item[2])
                prot = float(item[3]) if len(item) > 3 else 0.0
            elif tag == "size":
                sx = float(item[1])
                sy = float(item[2])
            elif tag == "layers":
                layers = [str(l) for l in item[1:]]
            elif tag == "net":
                net_code = int(item[1])
                net_name = str(item[2]) if len(item) > 2 else None

        return Pad(
            number=number,
            pad_type=pad_type,
            shape=shape,
            x=px,
            y=py,
            rotation=prot,
            size=(sx, sy),
            layers=layers,
            net_code=net_code,
            net_name=net_name,
        )

    def _parse_segment(self, node: List[Any]) -> TrackSegment:
        start = (0.0, 0.0)
        end = (0.0, 0.0)
        width = 0.25
        layer = "F.Cu"
        net_code = 0

        for item in node[1:]:
            if not isinstance(item, list) or not item:
                continue

            tag = item[0]
            if tag == "start":
                start = (float(item[1]), float(item[2]))
            elif tag == "end":
                end = (float(item[1]), float(item[2]))
            elif tag == "width":
                width = float(item[1])
            elif tag == "layer":
                layer = str(item[1])
            elif tag == "net":
                net_code = int(item[1])

        return TrackSegment(start=start, end=end, width=width, layer=layer, net_code=net_code)

    def _parse_via(self, node: List[Any]) -> Via:
        at = (0.0, 0.0)
        size = 0.8
        drill = 0.4
        layers = ("F.Cu", "B.Cu")
        net_code = 0

        for item in node[1:]:
            if not isinstance(item, list) or not item:
                continue

            tag = item[0]
            if tag == "at":
                at = (float(item[1]), float(item[2]))
            elif tag == "size":
                size = float(item[1])
            elif tag == "drill":
                drill = float(item[1])
            elif tag == "layers":
                layers = (str(item[1]), str(item[2]))
            elif tag == "net":
                net_code = int(item[1])

        return Via(at=at, size=size, drill=drill, layers=layers, net_code=net_code)


# ==============================================================================
# Streamlit Application
# ==============================================================================

# --- Configuration ---
st.set_page_config(
    page_title="PragyanAI Autonomous EDA",
    page_icon="🤖",
    layout="wide"
)

# --- Global State Management ---
if 'project_id' not in st.session_state:
    st.session_state.project_id = f"PRJ-{datetime.now().strftime('%y%m%d-%H%M')}"
if 'current_step' not in st.session_state:
    st.session_state.current_step = "Planning"
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'parsed_pcb' not in st.session_state:
    st.session_state.parsed_pcb = None

# --- Custom Styling ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# --- Navigation Sidebar ---
with st.sidebar:
    st.image("https://via.placeholder.com/150?text=PragyanAI", width=120)
    st.title("Studio Workflow")
    activity = st.radio(
        "Go to Activity:",
        [" 1. Project Planning",  "2. Implementation", " 3. Lab Analysis", " 4. Fulfillment"]
    )
    st.divider()
    st.info(f"Active Project: **{st.session_state.project_id}**")

# --- Activity 1: Planning ---
if activity == " Project Planning":
    st.header("Step 1: AI Requirements & Architecture")
    col_input, col_out = st.columns([1, 1])

    with col_input:
        st.subheader("Design Prompt")
        user_prompt = st.text_area(
            "Describe your hardware in plain English:",
            "A high-efficiency ESP32 module with 12V input, I2C headers, and a battery charging circuit.",
            height=200
        )
        if st.button("Initialize Agents", type="primary"):
            st.session_state.logs.append(f"Planning Agent started for: {user_prompt}")
            st.success("Planning complete! Check Architecture Plan.")

    with col_out:
        st.subheader("Architecture Preview")
        mock_arch = {
            "Power Tree": "12V -> Buck (5V) -> LDO (3.3V)",
            "MCU": "ESP32-S3-WROOM-1",
            "Interfaces": ["I2C", "UART", "ADC"],
            "Layers": 4
        }
        st.json(mock_arch)

# --- Activity 2: Implementation ---
elif activity == " Implementation":
    st.header("Step 2: Circuit Construction & Sourcing")

    # --- Live PCB File Upload & Pure Python Parsing ---
    st.subheader("KiCad PCB Layout Ingestion")
    uploaded_pcb = st.file_uploader("Upload .kicad_pcb File (Optional)", type=["kicad_pcb"])

    if uploaded_pcb is not None:
        try:
            pcb_text = uploaded_pcb.getvalue().decode("utf-8", errors="ignore")
            parser = KiCadPCBParser(pcb_text, is_raw_text=True)
            pcb_data = parser.parse()
            st.session_state.parsed_pcb = pcb_data
            st.session_state.logs.append(f"Successfully parsed KiCad PCB: {uploaded_pcb.name} (Nets: {len(pcb_data.nets)}, Footprints: {len(pcb_data.footprints)})")
            st.success(f"Successfully parsed **{uploaded_pcb.name}** (KiCad format version {pcb_data.version})")
        except Exception as e:
            st.error(f"Error parsing KiCad PCB file: {e}")

    # Metrics Row if PCB data is loaded
    if st.session_state.parsed_pcb:
        pcb = st.session_state.parsed_pcb
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Total Nets", len(pcb.nets))
        p2.metric("Components", len(pcb.footprints))
        p3.metric("Tracks", len(pcb.tracks))
        p4.metric("Vias", len(pcb.vias))

    col_bom, col_place = st.columns(2)

    with col_bom:
        st.subheader("BOM Audit")
        if st.session_state.parsed_pcb and st.session_state.parsed_pcb.footprints:
            # Build BOM directly from the parsed .kicad_pcb
            bom_rows = [
                {
                    "Ref": fp.reference or "N/A",
                    "Part": fp.value or fp.footprint_name,
                    "Layer": fp.layer,
                    "Pads": len(fp.pads),
                    "Status": "Parsed from PCB"
                }
                for fp in st.session_state.parsed_pcb.footprints
            ]
            st.dataframe(pd.DataFrame(bom_rows), use_container_width=True)
        else:
            # Fallback mock data
            bom_df = pd.DataFrame({
                "Ref": ["U1", "U2", "C1", "R1"],
                "Part": ["ESP32-WROOM", "MP2315", "22uF", "10k"],
                "Status": ["In Stock", "In Stock", "In Stock", "In Stock"],
                "Price (USD)": [3.40, 1.20, 0.05, 0.01]
            })
            st.table(bom_df)

    with col_place:
        st.subheader("Placement Strategy")
        if st.session_state.parsed_pcb and st.session_state.parsed_pcb.footprints:
            placement_summary = {
                fp.reference: {"x": round(fp.x, 2), "y": round(fp.y, 2), "rot": round(fp.rotation, 1)}
                for fp in st.session_state.parsed_pcb.footprints[:10]
            }
            st.json(placement_summary)
            st.caption(f"Showing coordinates for first {min(10, len(st.session_state.parsed_pcb.footprints))} components.")
        else:
            st.code("""
            // placement.json
            "U1": {"x": 25.0, "y": 25.0, "rot": 0},
            "J1": {"x": 0.0, "y": 12.5, "rot": 270}
            """, language="json")
            st.info("Component spacing checked against FootprintAnalyzer.")

# --- Activity 3: Lab Analysis ---
elif activity == " Lab Analysis":
    st.header("Step 3: Physics-Based Verification")

    m1, m2, m3 = st.columns(3)
    m1.metric("Max Temperature", "48.2°C", "-2.1°C")
    m2.metric("Signal Integrity", "98.4%", "+1.2%")
    m3.metric("DRC Errors", "0", "Critical")

    st.subheader("Thermal Gradient Map")
    st.image("https://via.placeholder.com/800x300.png?text=PCB+Thermal+Heatmap+Simulation", use_container_width=True)

    with st.expander("View SI/PI Testbench Logs"):
        st.text("Executing Transient Analysis on +3.3V Rail...\nStabilization: 12ms\nRipple: 15mV (PASS)")

# --- Activity 4: Fulfillment ---
elif activity == " Fulfillment":
    st.header("Step 4: Manufacturing Pack & Documentation")

    st.info("All validation gates have been PASSED. Files are ready for production.")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("Production Files")
        st.download_button(" Download Gerber ZIP", "mock_data", file_name="Gerbers_RevA.zip")
        st.caption("Standard ODB++ & Drill files included.")

    with c2:
        st.subheader("Technical Docs")
        st.download_button(" Design Validation Report", "mock_data", file_name="DVR_Report.md")
        st.caption("Includes Thermal and SI/PI traces.")

    with c3:
        st.subheader("Factory Handover")
        st.button(" Push to JLCPCB API", disabled=True)
        st.caption("Direct factory API integration (V2 Feature).")

# --- Activity Logger (Bottom of all pages) ---
st.divider()
with st.expander(" System Master Logs"):
    for log in st.session_state.logs:
        st.text(log)
        
