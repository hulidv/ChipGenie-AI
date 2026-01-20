from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException

from .bom import generate_bom, generate_bom_ai
from .component_db import ComponentStore
from .models import DesignResponse, ProjectRequest
from .nlu import parse_request
from .schematic import synthesize_schematic
from .simulation import simulate_design

app = FastAPI(title="ChipGenie AI", version="0.1.0")


def get_store() -> ComponentStore:
    store = ComponentStore()
    try:
        store.load()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return store


@app.post("/design", response_model=DesignResponse)
def design_endpoint(payload: ProjectRequest, store: ComponentStore = Depends(get_store)) -> DesignResponse:
    parsed = parse_request(payload)
    bom = generate_bom(parsed, store)
    schematic = synthesize_schematic(parsed, bom)
    return DesignResponse(parsed_spec=parsed, bom=bom, schematic=schematic)


@app.post("/design/ai", response_model=DesignResponse)
async def design_ai_endpoint(payload: ProjectRequest, store: ComponentStore = Depends(get_store)) -> DesignResponse:
    parsed = parse_request(payload)
    bom = await generate_bom_ai(parsed, store)
    schematic = synthesize_schematic(parsed, bom)
    _ = simulate_design(parsed)
    return DesignResponse(parsed_spec=parsed, bom=bom, schematic=schematic)
