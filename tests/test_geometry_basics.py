import sys
import os
import copy

import pytest
import numpy as np

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_dir + "/..")
sys.path.append(current_dir + "/../src/Carnutes")

from utils import geometry as geo
from utils import database_reader, tree, geometrical_operations


@pytest.fixture
def get_skeleton_length():
    yield tree.SKELETON_LENGTH


@pytest.fixture
def get_database():
    reader = database_reader.DatabaseReader(
        current_dir + "/../src/Carnutes/database/tree_database.fs"
    )
    yield reader
    reader.close()


def test_Pointcloud():
    point_cloud = geo.Pointcloud([[1, 2, 3], [4, 5, 6]])
    assert point_cloud.points == [[1, 2, 3], [4, 5, 6]]
    assert point_cloud.colors == None


def test_Mesh():
    vertices_list = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, 0]]
    faces_list = [[0, 1, 2], [0, 1, 3]]
    mesh = geo.Mesh(vertices_list, faces_list)
    assert mesh.vertices[0] == [1, 0, 0]
    assert len(mesh.vertices) == 4
    assert mesh.faces[0] == [0, 1, 2]
    assert len(mesh.faces) == 2
    assert mesh.colors == None


def test_database_reader(get_database):
    reader = get_database
    tree_id = 0
    my_tree = reader.get_tree(tree_id)
    my_tree = copy.deepcopy(my_tree)
    reader.close()
    assert my_tree.id == 0
    assert my_tree.name == "46.590369,6.710846"


def test_point_cloud(get_skeleton_length, get_database):
    reader = get_database
    tree_id = 0
    my_tree = reader.get_tree(tree_id)
    my_tree = copy.deepcopy(my_tree)
    reader.close()
    assert len(my_tree.skeleton.points) == get_skeleton_length
    assert (
        len(my_tree.point_cloud.points) > 1000
    )  # The number of points will depend on the voxel size used to create the point cloud.
    assert (
        len(my_tree.point_cloud.points) < 30000
    )  # the tree point cloud should never have more than 30000 points
    assert len(my_tree.point_cloud.colors) == len(my_tree.point_cloud.points)


def test_project_points_to_plane():
    points = [[1, 1, 1], [2, 2, 2], [3, 3, 3]]
    plane_origin = [0, 0, 0]
    plane_normal = [0, 0, 1]
    projected_points = geometrical_operations.project_points_to_plane(
        points, plane_origin, plane_normal
    )
    assert projected_points == [[1, 1, 0], [2, 2, 0], [3, 3, 0]]


def test_fit_circle_with_open3d():
    points = [
        [
            2 * (np.cos(alfa) * np.cos(np.pi / 4)) + 1,
            2 * np.sin(alfa) + 2,
            2 * (np.cos(alfa) * np.sin(np.pi / 4)) + 3,
        ]
        for alfa in np.linspace(0, 2 * np.pi, 100)
    ]
    center, radius = geometrical_operations.fit_circle_with_open3d(points)
    assert center[0] == pytest.approx(1, abs=2e-1)
    assert center[1] == pytest.approx(2, abs=2e-1)
    assert center[2] == pytest.approx(3, abs=2e-1)
    assert radius == pytest.approx(2, abs=3e-1)
