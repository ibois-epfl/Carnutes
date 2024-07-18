"""
Module storing the Tree class and the geometry classes
"""
#! python3
import persistent
from collections import defaultdict

import numpy as np
import open3d as o3d
# from pc_skeletor import *
# from pc_skeletor import LBC

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
        return f"Point cloud {self.point_cloud_id} - {self.point_cloud_name}"



class Tree(persistent.Persistent):
    """
    Tree class to store tree data.
    The point cloud of the tree is stored as a list of points
    :param tree_id
        The id of the tree
    :param tree_name
        The name of the tree
    :param tree_point_cloud
        The point cloud of the tree as a list of lists of 3 coordinates
    :param point_cloud_colors
        The colors of the point cloud as a list of lists of 3 colors. None by default.
    :param tree_skeleton
        The skeleton of the tree as a list of lists of 3 coordinates. None by default.
    """
    def __init__(self, 
                 id : int,
                 name : str,
                 point_cloud : Pointcloud,
                 skeleton : Pointcloud = None):
        self.id = id
        self.name = name
        self.point_cloud = point_cloud
        self.skeleton = skeleton

    def compute_skeleton(self):
        """
        Compute the skeleton of the point cloud.
        For now it is done in a rather sloppy way. this is because pc_skeletor is currently causing issues

        To Do: make this actually professional

        :param voxel_size: float, optional
            The size of the voxel grid used for downsampling the point cloud. The default is 0.01.
        """
        skeleton_as_list = []

        o3d_pc = o3d.geometry.PointCloud()
        o3d_pc.points = o3d.utility.Vector3dVector(self.point_cloud.points)
    
        oriented_bounding_box = o3d_pc.get_oriented_bounding_box()
        min_bound = oriented_bounding_box.get_min_bound()[2]
        pc_height = oriented_bounding_box.get_max_bound()[2] - min_bound
        print("height of the point cloud is ", pc_height)
        segments = defaultdict(list)
        for point in np.asarray(o3d_pc.points):
            relative_height = point[2] - min_bound
            # We create 10 indexes along the height of the point cloud (we assume the tree upwards)
            index = int(round(10 * relative_height/pc_height))
            if index not in segments:
                segments[index] = [point]
            else:
                segments[index].append(point)
        for i in range(11):
            i_th_segment = segments[i]
            center_point = i_th_segment[0]
            for j in range(len(i_th_segment) - 1):
                center_point += i_th_segment[i + 1]
            center_point /= len(i_th_segment)
            skeleton_as_list.append(center_point)

        self.skeleton = skeleton_as_list

        # print("Skeleton computed, n° points = ", len(self.skeleton.points))
        return self.skeleton

    def __str__(self):
        return f"Tree {self.id} - {self.name}"