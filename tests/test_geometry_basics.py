import sys
import os
import copy
import pytest

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_dir + "/..")
sys.path.append(current_dir + "/../src")

from src.utils import geometry as geo
from src.utils import database_reader
from src.utils import tree

@pytest.fixture
def get_skeleton_length():
    yield tree.SKELETON_LENGTH

def test_Pointcloud():
    point_cloud = geo.Pointcloud([[1, 2, 3], [4, 5, 6]])
    assert point_cloud.points == [[1, 2, 3], [4, 5, 6]]
    assert point_cloud.colors == None

def test_Mesh():
    vertices_list = [[1, 0, 0], 
                     [0, 1, 0], 
                     [0, 0, 1],
                     [0, 0, 0]]
    faces_list = [[0, 1, 2],
                  [0, 1, 3]]
    mesh = geo.Mesh(vertices_list, faces_list)
    assert mesh.vertices[0] == [1, 0, 0]
    assert len(mesh.vertices) == 4
    assert mesh.faces[0] == [0, 1, 2]
    assert len(mesh.faces) == 2
    assert mesh.colors == None

def test_point_cloud(get_skeleton_length):
    reader = database_reader.DatabaseReader(current_dir + "/../src/database/tree_database.fs")
    tree_id = 0
    my_tree = reader.get_tree(tree_id)
    my_tree = copy.deepcopy(my_tree)
    reader.close()
    assert len(my_tree.skeleton.points) == get_skeleton_length
    assert len(my_tree.point_cloud.points) == 6388
    assert len(my_tree.point_cloud.colors) == len(my_tree.point_cloud.points)
