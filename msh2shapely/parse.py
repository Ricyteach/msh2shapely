from itertools import cycle, tee
from typing import List, Dict

from mytools import flatten

from .items import Msh, Node, Element, Boundary
from .msh import MshParser
from shapely.geometry import Point, LineString, MultiLineString

parser = MshParser[Msh](Msh, Node, Element, Boundary)


def node_dict(node_list: List[Node]) -> Dict[int, Point]:
    """A dictionary from a node list that turns a node number into a shapely Point"""

    return {n.num:Point(n.x,n.y) for n in node_list}


def element_dict(element_list: List[Element], node_dict: Dict[int, Point]) -> Dict[int, MultiLineString]:
    """A dictionary from an element list that turns an element number into a shapely MultiLineString"""

    d: Dict[int, MultiLineString] = dict()

    for e in element_list:
        if len(e)==2:
            line_strings = (LineString((node_dict[e.i], node_dict[e.j])),)
        else:
            lhs, rhs = e[:-1], e[1:]+e[:1]
            line_strings = tuple(LineString((node_dict[n1], node_dict[n2])) for n1,n2 in zip(lhs, rhs))
        d[e.num] = MultiLineString(line_strings)

    return d


def elements2multilinestring(msh: str) -> MultiLineString:
    """A MultiLineString representing all of the line segments in the Msh object."""

    msh_obj = parser.loads(msh)
    nd = node_dict(msh_obj.nodes)
    ed = element_dict(msh_obj.elements, nd)
    return MultiLineString(tuple(flatten(ed.values())))
