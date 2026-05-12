import re
import os
import json
from typing import Dict, Optional

class SymbolExtractor:
    """
    Parses KiCad .kicad_sym files to extract pin information 
    and metadata for AI-driven schematic generation.
    """

    def __init__(self, library_path: str):
        self.library_path = library_path

    def _load_library(self) -> str:
        """Reads the raw content of the symbol library file."""
        if not os.path.exists(self.library_path):
            raise FileNotFoundError(f"Library not found at: {self.library_path}")
        
        with open(self.library_path, 'r', encoding='utf-8') as f:
            return f.read()

    def get_symbol_pins(self, symbol_name: str) -> Dict[str, str]:
        """
        Scans the library for a specific symbol and returns a 
        dictionary mapping Pin Names to Pin Numbers.
        """
        content = self._load_library()
        
        # Regex to isolate the block for a specific symbol
        # It looks for (symbol "Name" ... ) and stops at the closing parenthesis of the main block
        symbol_pattern = rf'\(symbol "{symbol_name}"\s.*?\n\s+\(symbol "{symbol_name}_0_1"(.*?)\n\s+\)'
        match = re.search(symbol_pattern, content, re.DOTALL)
        
        if not match:
            print(f"⚠️ Warning: Symbol '{symbol_name}' not found in {self.library_path}")
            return {}

        symbol_inner_content = match.group(1)

        # Regex to extract Pin Name and Pin Number from the S-expression
        # Matches: (pin power_in line (at ...) (name "VDD" ...) (number "1" ...))
        pin_pattern = r'\(pin \w+ \w+ \(at .*?\) \(name "(.*?)" .*?\) \(number "(.*?)"'
        pins = re.findall(pin_pattern, symbol_inner_content)
        
        return {name: number for name, number in pins}

    def get_symbol_properties(self, symbol_name: str) -> Dict[str, str]:
        """
        Extracts properties like Footprint, Value, and Datasheet 
        from the symbol definition.
        """
        content = self._load_library()
        
        # Locate the specific symbol block
        symbol_block_pattern = rf'\(symbol "{symbol_name}"\s.*?\)'
        # We search specifically for the property lines within that block
        property_pattern = r'\(property "(.*?)" "(.*?)" \(id \d+\)'
        
        # First, find the whole symbol block to avoid cross-contamination
        block_match = re.search(rf'\(symbol "{symbol_name}"\s.*?\n(.*?)\s+\(symbol', content, re.DOTALL)
        if not block_match:
            return {}
            
        properties = re.findall(property_pattern, block_match.group(1))
        return {prop[0]: prop[1] for prop in properties}

# --- Usage Example for Agents ---
if __name__ == "__main__":
    # Path to the enterprise core library
    core_lib_path = "design/lib/symbols/enterprise_core.kicad_sym"
    
    try:
        extractor = SymbolExtractor(core_lib_path)
        
        # 1. Get Pin Mapping
        pins = extractor.get_symbol_pins("AMS1117-3.3")
        print(f"📍 Pins for AMS1117-3.3: {json.dumps(pins, indent=2)}")
        
        # 2. Get Metadata
        props = extractor.get_symbol_properties("AMS1117-3.3")
        print(f"ℹ️ Properties for AMS1117-3.3: {json.dumps(props, indent=2)}")
        
    except FileNotFoundError as e:
        print(e)
