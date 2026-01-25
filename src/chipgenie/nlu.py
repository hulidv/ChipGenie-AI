from __future__ import annotations

import re
from typing import Dict, Optional, Union

from pydantic import BaseModel

from .models import DesignConstraint, ParsedSpec, ProjectRequest


class NluConfig(BaseModel):
    use_llm: bool = False
    model: Optional[str] = None


def _heuristic_constraints(text: str) -> DesignConstraint:
    lower = text.lower()
    voltage_match = re.search(r"(\d+(?:\.\d+)?)\s*v", lower)
    current_match = re.search(r"(\d+(?:\.\d+)?)\s*a", lower)
    frequency_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:hz|khz|mhz)", lower)
    frequency = None
    if frequency_match:
        raw = frequency_match.group(1)
        frequency = float(raw)
        if "khz" in lower:
            frequency *= 1_000
        elif "mhz" in lower:
            frequency *= 1_000_000
    return DesignConstraint(
        voltage=float(voltage_match.group(1)) if voltage_match else None,
        current=float(current_match.group(1)) if current_match else None,
        frequency=frequency,
    )


def parse_request(request: ProjectRequest, config: Optional[NluConfig] = None) -> ParsedSpec:
    config = config or NluConfig()
    constraints = _heuristic_constraints(request.description)
    requirements: Dict[str, Union[float, str]] = {}
    if request.form_factor:
        requirements["form_factor"] = request.form_factor
    if request.interfaces:
        requirements["interfaces"] = ",".join(request.interfaces)
    if request.constraints.voltage and not constraints.voltage:
        constraints.voltage = request.constraints.voltage
    if request.constraints.current and not constraints.current:
        constraints.current = request.constraints.current
    if request.constraints.frequency and not constraints.frequency:
        constraints.frequency = request.constraints.frequency
    if request.constraints.temperature:
        constraints.temperature = request.constraints.temperature
    intent = request.description.strip()
    return ParsedSpec(
        intent=intent,
        constraints=constraints,
        requirements=requirements,
        notes=request.notes,
    )
