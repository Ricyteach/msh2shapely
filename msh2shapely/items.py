from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Sequence, overload, Iterator


class ElementError(Exception):
    pass


@dataclass
class Msh:
    nodes: List[Node]
    elements: List[Element]
    boundaries: List[Boundary]


@dataclass
class Node:
    num: int
    x: float
    y: float


@dataclass
class Element(Sequence[int]):
    num: int
    i: int
    j: int
    k: int = 0
    l: int = 0

    def __post_init__(self):
        if self.k==0 and self.l!=0:
            raise ElementError("misnumbered element")
        i=0
        for i,_ in enumerate(self, 1):
            pass
        self._len = i

    def __iter__(self) -> Iterator[int]:

        for n in (getattr(self, n) for n in "ijkl"):
            if n!=0:
                yield n

    def __len__(self) -> int:
        return self._len

    @overload
    @abstractmethod
    def __getitem__(self, i: int) -> int: ...

    @overload
    @abstractmethod
    def __getitem__(self, s: slice) -> Sequence[int]: ...

    def __getitem__(self, x):
        return list(self)[x]


@dataclass
class Boundary:
    num: int
    node: int
