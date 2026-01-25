from __future__ import annotations

from typing import List

from .llm_providers import LLMClient
from .models import BomLine, ParsedSpec


async def propose_topology(spec: ParsedSpec, bom: List[BomLine]) -> dict:
    llm = LLMClient()
    system = (
        "You output a minimal JSON topology: {blocks:[{ref,type,mpn}],connections:[{from,to}]}. "
        "Keep it simple and consistent with BOM."
    )
    user = f"Intent: {spec.intent}\nBOM: {[line.component.mpn for line in bom]}"
    try:
        text = await llm.chat(system, user)
    except Exception:
        text = ""
    if not text or "blocks" not in text:
        blocks = [
            {"ref": f"U{i+1}", "type": line.component.type, "mpn": line.component.mpn}
            for i, line in enumerate(bom)
        ]
        return {
            "blocks": blocks,
            "connections": [{"from": "VIN", "to": blocks[0]["ref"] if blocks else "U1"}],
        }
    return {"raw": text}
