from __future__ import annotations

import shutil
from typing import Dict

from .models import ParsedSpec


def simulate_design(spec: ParsedSpec) -> Dict:
    has_ngspice = shutil.which("ngspice") is not None
    if not has_ngspice:
        return {"status": "skipped", "reason": "ngspice not installed"}
    # Stub: In future, generate netlist and run ngspice; here we return a placeholder
    return {"status": "pending", "note": "netlist generation not implemented yet"}
