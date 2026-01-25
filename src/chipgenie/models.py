from __future__ import annotations

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class DesignConstraint(BaseModel):
    voltage: Optional[float] = Field(None, description="Target voltage in volts")
    current: Optional[float] = Field(None, description="Target current in amperes")
    frequency: Optional[float] = Field(None, description="Target frequency in hertz")
    temperature: Optional[str] = Field(
        None, description="Operating temperature range, e.g. -40C to 85C"
    )


class ProjectRequest(BaseModel):
    description: str = Field(..., description="User-provided free-form goal")
    form_factor: Optional[str] = None
    interfaces: List[str] = Field(default_factory=list)
    constraints: DesignConstraint = Field(default_factory=DesignConstraint)
    notes: Optional[str] = None


class Component(BaseModel):
    mpn: str
    name: str
    type: str
    params: Dict[str, Union[float, str]]
    footprint: Optional[str] = None
    supplier_url: Optional[str] = None
    cost: Optional[float] = None


class BomLine(BaseModel):
    line: int
    quantity: int
    component: Component
    notes: Optional[str] = None


class ParsedSpec(BaseModel):
    intent: str
    constraints: DesignConstraint
    requirements: Dict[str, Union[float, str]]
    notes: Optional[str] = None


class SchematicArtifact(BaseModel):
    format: str = Field(..., description="e.g. kicad_sch, json")
    path: Optional[str] = Field(None, description="Filesystem path if persisted")
    preview: Optional[Dict] = Field(None, description="In-memory preview for UI")


class DesignResponse(BaseModel):
    parsed_spec: ParsedSpec
    bom: List[BomLine]
    schematic: SchematicArtifact
