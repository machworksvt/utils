import json
import os
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import openvsp as vsp
from rich.console import Console

console = Console()

"""
    Data classes for components
"""

@dataclass
class MassConfiguration:
    name: str = "Mass Configuration"
    cg: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    mass: float = 0.0
    inertia_matrix: List[List[float]] = field(default_factory=lambda: [[0.0]*3 for _ in range(3)])

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)