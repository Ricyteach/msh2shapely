# msh2shapely
Tool for reading (Mesh2D, non Gmsh) .msh files and turning them into shapely objects. 

Install:

```bash
pip install git+https://github.com/Ricyteach/msh2shapely
```

Usage for `elements2multilinestring`:

```python
from msh2shapely import elements2multilinestring

s = """ 
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
1    1"""[1:]

multi_line_string = elements2multilinestring(s)
```