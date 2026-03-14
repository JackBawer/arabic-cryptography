from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Candidate:
    plaintext: str
    score: float
    key_description: str
