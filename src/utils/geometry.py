"""
module for geometry classes
"""
from dataclasses import dataclass
import typing

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
    def __init__(self,
                 points : typing.List[typing.List[float]], 
                 colors : typing.List[typing.List[int]] = None):
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
    def __init__(self,
                 vertices : typing.List[typing.List[float]],
                 faces : typing.List[typing.List[int]],
                 colors : typing.List[typing.List[int]] = None):
        self.vertices = vertices
        self.faces = faces
        self.colors = colors

    def __str__(self):
        return "Mesh with {} vertices and {} faces".format(len(self.vertices), len(self.faces))