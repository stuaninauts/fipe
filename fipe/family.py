"""Model family from the FIPE model name, to compare versions of the same model (entry vs top of the range).

FIPE names a version as "<model> <engine> <trim> ...", e.g. "Gol 1.0 Mi 8V" or
"Corolla XEi 2.0 Flex 16V Aut.". The family is the brand plus the first word of the name, with two exceptions:
- marketing prefixes that do not name a model ("New Beetle", "Nova Saveiro") are skipped;
- "Grand" names its own model together with the next word ("Grand Siena" is not a "Siena").
It is a heuristic: tests/test_family.py pins the cases it must get right.
"""

from __future__ import annotations

import re

SKIP = {"NEW", "NOVA", "NOVO", "NUEVO"}
JOIN_NEXT = {"GRAND"}
_TOKEN = re.compile(r"[^\wÀ-ÿ]+")


def family(brand: str, model: str) -> str | None:
    words = [w for w in _TOKEN.split(model.upper()) if w]
    while words and words[0] in SKIP:
        words = words[1:]
    if not words:
        return None
    name = " ".join(words[:2]) if words[0] in JOIN_NEXT and len(words) > 1 else words[0]
    return f"{brand.strip()}|{name}"
