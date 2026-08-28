"""
Pure-Python KiCad PCB S-Expression Parser
Zero external build dependencies. Compatible with KiCad v6+ files.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


# ==========================================
# 1. Low-Level S-Expression Tokenizer/Parser
# ==========================================

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


# ==========================================
# 2. Data Models for PCB Elements
# ==========================================

@dataclass
class Net:
    code: int
    name: str


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
    version: Optional[int]
    generator: Optional[str]
    nets: Dict[int, str] = field(default_factory=dict)
    footprints: List[Footprint] = field(default_factory=list)
    tracks: List[TrackSegment] = field(default_factory=list)
    vias: List[Via] = field(default_factory=list)


# ==========================================
# 3. High-Level PCB Extractor
# ==========================================

class KiCadPCBParser:
    """Parses .kicad_pcb files into structured Python objects."""

    def __init__(self, filepath: Union[str, Path]):
        self.filepath = Path(filepath)
        self.raw_ast: List[Any] = []
        self.pcb: Optional[ParsedPCB] = None

    def parse(self) -> ParsedPCB:
        with open(self.filepath, "r", encoding="utf-8") as f:
            content = f.read()

        self.raw_ast = parse_sexpr(content)
        if not self.raw_ast or self.raw_ast[0] != "kicad_pcb":
            raise ValueError(f"Invalid KiCad PCB file: {self.filepath}")

        pcb = ParsedPCB(version=None, generator=None)

        for node in self.raw_ast[1:]:
            if not isinstance(node, list) or not node:
                continue

            tag = node[0]

            if tag == "version":
                pcb.version = node[1]
            elif tag == "generator":
                pcb.generator = node[1]
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
            elif sub_tag == "fp_text" or sub_tag == "property":
                text_type = str(item[1])
                text_val = str(item[2]) if len(item) > 2 else ""
                if text_type == "reference" or text_type == "Reference":
                    reference = text_val
                elif text_type == "value" or text_type == "Value":
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
