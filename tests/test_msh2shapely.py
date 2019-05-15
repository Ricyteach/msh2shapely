from pytest import fixture

from msh2shapely import elements2multilinestring


@fixture
def msh_example():
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
    return s


def test_elements2multilinestring(msh_example):
    assert elements2multilinestring(msh_example)
