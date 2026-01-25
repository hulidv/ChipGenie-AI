from __future__ import annotations

from typing import List

from .models import BomLine, ParsedSpec, SchematicArtifact


def synthesize_schematic(spec: ParsedSpec, bom: List[BomLine]) -> SchematicArtifact:
    blocks = []
    for line in bom:
        blocks.append(
            {
                "ref": f"U{line.line}",
                "type": line.component.type,
                "mpn": line.component.mpn,
                "footprint": line.component.footprint,
                "role": line.notes,
            }
        )
    preview = {
        "intent": spec.intent,
        "constraints": spec.constraints.model_dump(),
        "blocks": blocks,
        "connections": [
            {"from": "VIN", "to": blocks[0]["ref"] if blocks else "U1"},
            {"from": blocks[0]["ref"] if blocks else "U1", "to": "VOUT"},
        ],
    }
    return SchematicArtifact(format="json", preview=preview)
