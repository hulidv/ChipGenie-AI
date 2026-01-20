from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Optional

from .llm_providers import LLMClient
from .models import Component, ParsedSpec
from .search_providers import SearchClient

CACHE_FILE = Path(__file__).resolve().parents[2] / "data" / "fetched_cache.json"


def _load_cache() -> List[Component]:
    if not CACHE_FILE.exists():
        return []
    try:
        payload = json.loads(CACHE_FILE.read_text("utf-8"))
        return [Component(**item) for item in payload]
    except Exception:
        return []


def _save_cache(components: List[Component]) -> None:
    data = [c.model_dump() for c in components]
    CACHE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _extract_candidate_mpns(text: str) -> List[str]:
    mpns = re.findall(r"[A-Z0-9-]{4,}\w", text)
    return list(dict.fromkeys(mpns))


async def fetch_components_ai(spec: ParsedSpec, llm: LLMClient, search: SearchClient) -> List[Component]:
    system = (
        "You assist with electronic component sourcing. Given intent and constraints, "
        "propose specific part numbers and a search query. Return a concise list."
    )
    user = f"Intent: {spec.intent}\nConstraints: {spec.constraints.model_dump()}"
    try:
        suggestion = await llm.chat(system, user)
    except Exception:
        suggestion = "Search site:octopart.com for suitable parts."
    query = suggestion.strip()
    if spec.constraints.voltage:
        query += f" vout {spec.constraints.voltage}V"
    if spec.constraints.current:
        query += f" iout {spec.constraints.current}A"
    results = await search.search(query)
    components: List[Component] = []
    for r in results[:5]:
        mpns = _extract_candidate_mpns(r.title + " " + (r.snippet or ""))
        for mpn in mpns[:2]:
            components.append(
                Component(
                    mpn=mpn,
                    name=f"Candidate {mpn}",
                    type="unknown",
                    params={"source": r.url},
                    supplier_url=r.url,
                    footprint=None,
                    cost=None,
                )
            )
    if components:
        _save_cache(components)
    else:
        components = _load_cache()
    return components
