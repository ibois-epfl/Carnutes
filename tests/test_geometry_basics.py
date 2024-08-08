import sys
import os
current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_dir + "/..")

from src.utils import geometry as geo

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