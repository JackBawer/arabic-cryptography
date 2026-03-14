from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class Alphabet(ABC):
    @abstractmethod
    def name(self) -> str:
        # 'english', 'french', 'arabic'
        raise NotImplementedError

    @abstractmethod
    def size(self) -> int:
        # 26 for English/French, 28 for Arabic
        raise NotImplementedError

    @abstractmethod
    def char_to_index(self, c: str) -> Optional[int]:
        # Map char to its index in the alphabet
        # Returns None if the char is not part of the alphabet
        raise NotImplementedError

    @abstractmethod
    def index_to_char(self, i: int) -> Optional[str]:
        # Map index back to a char in the alphabet
        # Returns None if i is out of bounds
        raise NotImplementedError

    def contains(self, c: str) -> bool:
        # True if c is a letter int his alphabet (after normalization)
        return self.char_to_index(c) is not None

    def chars(self) -> list[str]:
        # Return the full list of letters in the alphabet, in order
        out: list[str] = []
        for i in range(self.size()):
            ch = self.index_to_char(i)
            if ch is not None:
                out.append(ch)
        return out
