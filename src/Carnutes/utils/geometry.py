"""
module for geometry classes
"""

from dataclasses import dataclass
import typing


def sort_points(
    points_as_list: typing.List[typing.List[float]],
) -> typing.List[typing.List[float]]:
    """
    Sort a list of points by the coordinate along which there is maximum variation.
    """
    x_max_bounds = max([point[0] for point in points_as_list])
    x_min_bounds = min([point[0] for point in points_as_list])
    delta_x = x_max_bounds - x_min_bounds
    y_max_bounds = max([point[1] for point in points_as_list])
    y_min_bounds = min([point[1] for point in points_as_list])
    delta_y = y_max_bounds - y_min_bounds
    z_max_bounds = max([point[2] for point in points_as_list])
    z_min_bounds = min([point[2] for point in points_as_list])
    delta_z = z_max_bounds - z_min_bounds
    if delta_x > delta_y and delta_x > delta_z:
        points_as_list = sorted(points_as_list, key=lambda x: x[0])
    elif delta_y > delta_x and delta_y > delta_z:
        points_as_list = sorted(points_as_list, key=lambda x: x[1])
    elif delta_z > delta_x and delta_z > delta_y:
        points_as_list = sorted(points_as_list, key=lambda x: x[2])
    return points_as_list


@dataclass
class Pointcloud:
    """
    Pointcloud class to store point cloud data.
    The point cloud is stored as a list of points
    :param point_cloud
        The point cloud as a list of lists of 3 coordinates
    :param point_cloud_colors
        The colors of the point cloud as a list of lists of 3 colors. None by default.
    """

    def __init__(
        self,
        points: typing.List[typing.List[float]],
        colors: typing.List[typing.List[int]] = None,
    ):
        self.points = points
        self.colors = colors

    def __str__(self):
        return "Pointcloud with {} points".format(len(self.points))


@dataclass
class Mesh:
    """
    Mesh class to store mesh data.
    The mesh is stored as a list of vertices and a list of faces
    :param vertices
        The vertices of the mesh as a list of lists of 3 coordinates
    :param faces
        The faces of the mesh as a list of lists of 3 indices
    """

    def __init__(
        self,
        vertices: typing.List[typing.List[float]],
        faces: typing.List[typing.List[int]],
        colors: typing.List[typing.List[int]] = None,
    ):
        self.vertices = vertices
        self.faces = faces
        self.colors = colors

    def __str__(self):
        return "Mesh with {} vertices and {} faces".format(
            len(self.vertices), len(self.faces)
        )
