from __future__ import annotations

import argparse
import json
from typing import Any

from .bom import generate_bom
from .component_db import ComponentStore
from .models import DesignResponse, DesignConstraint, ProjectRequest
from .nlu import parse_request
from .schematic import synthesize_schematic


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ChipGenie AI CLI")
    parser.add_argument("description", help="Design goal, e.g. '3.3V regulator for 500mA'")
    parser.add_argument("--form-factor", dest="form_factor", help="Board form factor")
    parser.add_argument("--interface", dest="interfaces", action="append", default=[], help="Interface (repeatable)")
    parser.add_argument("--voltage", type=float, help="Target voltage in volts")
    parser.add_argument("--current", type=float, help="Target current in amperes")
    parser.add_argument("--frequency", type=float, help="Target frequency in hertz")
    parser.add_argument("--temperature", help="Temperature range")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output JSON")
    parser.add_argument("--ai", action="store_true", dest="use_ai", help="Use AI fetcher and topology")
    return parser.parse_args()


def run_once(args: argparse.Namespace) -> DesignResponse:
    constraints = DesignConstraint(
        voltage=args.voltage,
        current=args.current,
        frequency=args.frequency,
        temperature=args.temperature,
    )
    request = ProjectRequest(
        description=args.description,
        form_factor=args.form_factor,
        interfaces=args.interfaces,
        constraints=constraints,
    )
    store = ComponentStore()
    store.load()
    parsed = parse_request(request)
    if args.use_ai:
        from .bom import generate_bom_ai
        bom = __import__("asyncio").run(generate_bom_ai(parsed, store))
    else:
        from .bom import generate_bom
        bom = generate_bom(parsed, store)
    schematic = synthesize_schematic(parsed, bom)
    return DesignResponse(parsed_spec=parsed, bom=bom, schematic=schematic)


def main() -> None:
    args = _parse_args()
    response = run_once(args)
    if args.as_json:
        print(response.model_dump_json(indent=2))
    else:
        print("Intent:\n  " + response.parsed_spec.intent)
        print("Constraints:")
        for key, value in response.parsed_spec.constraints.model_dump().items():
            if value is not None:
                print(f"  {key}: {value}")
        print("BOM:")
        for line in response.bom:
            print(f"  {line.line}. {line.component.name} x{line.quantity} ({line.component.mpn})")
        print("Schematic preview (json):")
        print(json.dumps(response.schematic.preview, indent=2))


if __name__ == "__main__":
    main()
