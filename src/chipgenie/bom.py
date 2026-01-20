from __future__ import annotations

from typing import List

from .component_db import ComponentStore
from .models import BomLine, ParsedSpec, Component
from .component_fetcher import fetch_components_ai
from .llm_providers import LLMClient
from .search_providers import SearchClient


def generate_bom(spec: ParsedSpec, store: ComponentStore) -> List[BomLine]:
    lines: List[BomLine] = []
    line_no = 1
    regulator = None
    if spec.constraints.voltage:
        regulator = store.best_match(
            "regulator", {"vout": spec.constraints.voltage}
        ) or store.best_match("regulator")
    else:
        regulator = store.best_match("regulator")
    if regulator:
        lines.append(BomLine(line=line_no, quantity=1, component=regulator, notes="Vout rail"))
        line_no += 1
    for comp in store.find_by_type("capacitor"):
        if comp.params.get("capacitance") and float(comp.params["capacitance"]) >= 1e-6:
            lines.append(BomLine(line=line_no, quantity=2, component=comp, notes="Input/output decoupling"))
            line_no += 1
            break
    resistor = store.best_match("resistor")
    if resistor:
        lines.append(BomLine(line=line_no, quantity=2, component=resistor, notes="Dividers / pull-ups"))
    return lines


async def generate_bom_ai(spec: ParsedSpec, store: ComponentStore) -> List[BomLine]:
    llm = LLMClient()
    search = SearchClient()
    fetched: List[Component] = await fetch_components_ai(spec, llm, search)
    # Prefer AI-fetched parts if any; otherwise use heuristic BOM
    if not fetched:
        return generate_bom(spec, store)
    lines: List[BomLine] = []
    line_no = 1
    for comp in fetched[:3]:
        lines.append(BomLine(line=line_no, quantity=1, component=comp, notes="AI candidate"))
        line_no += 1
    return lines
