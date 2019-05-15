# -*- coding: utf-8 -*-

"""Tools for reading a .msh file to an object."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Callable, TypeVar, Sequence, Iterator, Generic, Type, List, Optional, Tuple
from .items import Node, Element, Boundary

MshObj = TypeVar("MshObj")
T = TypeVar("T")


def iter_nodes_elements_boundaries(lines: Iterable[str]) -> Iterator[List]:
    """Iterator of .msh sections, as a list of items."""

    for parser in (parse_node, parse_element, parse_boundary):
        yield list(iter_items(lines, parser))


def iter_items(lines: Iterable[str], parser: LineParser[T]) -> Iterator[T]:
    """Iterator of items from a .msh section. First line is the number of items to be iterated."""

    i_lines = iter(lines)
    n_items = next(iter_parsed(i_lines, parse_total))

    for _, parsed in zip(range(n_items), iter_parsed(i_lines, parser)):
        yield parsed


def iter_parsed(lines: Iterable[str], parser: Callable[[str], T]) -> Iterator[T]:
    """Iterator of parsed lines. Raises MshError() when a line is encountered that can't be parsed."""

    for line in lines:
        yield parser(line)


class MshError(Exception):
    pass


class ParseError(MshError):
    pass


@dataclass
class MshParser(Generic[MshObj]):
    """A parser that creates objects from .msh files"""

    msh_type: Type[MshObj]
    node_parser: Callable[[int, float, float], Node]
    element_parser: Callable[[int, int, int, int, int], Element]
    boundary_parser: Callable[[int, int], Boundary]

    def loads(self, s: str) -> MshObj:
        try:
            lines = s.splitlines()
        except AttributeError as e:
            raise MshError("s must be a string") from e
        else:
            return self.load(lines)

    def load(self, lines: Iterable[str]) -> MshObj:
        """Reads a .msh formatted file (example below) into a msh object.
        Example .msh format (commented and empty lines are optional/skipped):
            # nodes section
            # num x y
            3
            1    0.0    0.0
            2    1.0    1.0
            3    1.0    0.0
            # elements section
            # num i j [k [l]]
            2
            1    1    2
            2    1    2    3    0
            # boundaries section
            # num node
            1
            1    1
        """

        if isinstance(lines, str) or not isinstance(lines, Iterable):
            raise MshError(f"lines must be a non-str iterable, not {type(lines).__qualname__}")

        # skip commented or blank lines and strip whitespace
        i_lines = (line for line in (line.strip() for line in lines) if line and not line.startswith("#"))

        nodes, elements, boundaries = iter_nodes_elements_boundaries(i_lines)

        # check for leftover non-empty lines
        i: Optional[int] = None
        for i,_ in enumerate(i_lines, 1):
            pass
        if i is not None:
            raise MshError(f"There appear to be {i!s} extraneous data lines at the end of the file.")

        return self.msh_type(nodes=nodes, elements=elements, boundaries=boundaries)


@dataclass
class Field(Generic[T]):
    """A .msh file field."""

    name: str
    converter: Callable[[str], T]
    optional: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise MshError("field names must be strings")
        if not callable(self.converter):
            raise MshError("converter must be callable")
        if not isinstance(self.optional, bool):
            raise MshError("optional must be bool")


@dataclass(init=False)
class LineParser(Generic[T]):
    """A .msh file line parser."""

    fields: Sequence[Field]
    type: Callable[..., T]

    def __init__(self, *fields: Field, type: Callable[..., T]):

        self.fields = fields
        self.type = type

        # check that optional fields come after required fields
        first_optional_idx = len(fields)-len(self.optional)

        if self.required != fields[:first_optional_idx]:
            raise MshError("all optional fields must come after required fields")

    def __call__(self, line: str) -> T:

        val_strs = line.split()
        if len(val_strs) < len(self.required):
            e = ParseError("required fields are missing")
            e.line = line
            raise e
        if len(val_strs) > len(self.fields):
            e = ParseError("too many fields detected")
            e.line = line
            raise e
        try:
            return self.type(**{field.name: field.converter(value) for field, value in zip(self.fields, val_strs)})
        except Exception as e:
            raise ParseError("line parsing failed") from e

    @property
    def required(self) -> Tuple[Field, ...]:
        return tuple(f for f in self.fields if not f.optional)

    @property
    def optional(self) -> Tuple[Field, ...]:
        return tuple(f for f in self.fields if f.optional)


# .msh Field instances
tot = Field[int]("total", int)
num = Field[int]("num", int)
x = Field[float]("x", float)
y = Field[float]("y", float)
i = Field[int]("i", int)
j = Field[int]("j", int)
k = Field[int]("k", int, True)
l = Field[int]("l", int, True)
node = Field[int]("node", int)


def total_factory(total: int) -> int:
    return total


# .msh line parsers
parse_total = LineParser(tot, type=total_factory)
parse_node = LineParser(num, x, y, type=Node)
parse_element = LineParser(num, i, j, k, l, type=Element)
parse_boundary = LineParser(num, node, type=Boundary)
