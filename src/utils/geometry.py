"""
module for geometry classes
"""

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
                 points : list, 
                 colors : list = None):
        self.points = points
        self.colors = colors

    def __str__(self):
        return "Pointcloud with {} points".format(len(self.points))