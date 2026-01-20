from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Optional

from .models import Component

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
SEED_FILE = DATA_DIR / "components_seed.json"


class ComponentStore:
    def __init__(self, seed_path: Optional[Path] = None):
        self.seed_path = seed_path or SEED_FILE
        self.components: List[Component] = []

    def load(self) -> None:
        if not self.seed_path.exists():
            raise FileNotFoundError(f"Seed file missing: {self.seed_path}")
        with self.seed_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        self.components = [Component(**item) for item in payload]

    def find_by_type(self, ctype: str) -> List[Component]:
        return [c for c in self.components if c.type == ctype]

    def best_match(self, ctype: str, criteria: Optional[dict] = None) -> Optional[Component]:
        candidates = self.find_by_type(ctype)
        if not candidates:
            return None
        if not criteria:
            return candidates[0]
        scored = []
        for comp in candidates:
            score = 0
            for key, value in criteria.items():
                if str(comp.params.get(key)).lower() == str(value).lower():
                    score += 1
            scored.append((score, comp))
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1] if scored else None

    def all(self) -> Iterable[Component]:
        return list(self.components)
