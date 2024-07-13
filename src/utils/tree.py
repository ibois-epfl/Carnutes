"""
Module storing the Tree class and the Skeleton class
"""
#! python3
# r: pc_skeletor
import persistent

import open3d as o3d
from pc_skeletor import LBC

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
    :param tree_skeleton
        The skeleton of the tree as a list of lists of 3 coordinates. None by default.
    """
    def __init__(self, 
                 tree_id : int,
                 tree_name : str, 
                 tree_point_cloud : list, 
                 tree_skeleton : list =None):
        self.tree_id = tree_id
        self.tree_name = tree_name
        self.tree_point_cloud = tree_point_cloud
        self.tree_skeleton = tree_skeleton

    def compute_skeleton(self, voxel_size=0.01):
        """
        Compute the skeleton of the point cloud.

        :param voxel_size: float, optional
            The size of the voxel grid used for downsampling the point cloud. The default is 0.01.
        """
        skeleton_as_list = []

        # pc_skeletor needs an open3d point cloud but ZODB doesn't support it, hence this workaround
        o3d_pc = o3d.geometry.PointCloud()
        o3d_pc.points = o3d.utility.Vector3dVector(self.tree_point_cloud)
    
        lbc = LBC(o3d_pc, voxel_size)
        lbc.extract_skeleton()
        downsampled_skeleton = lbc.contracted_point_cloud.voxel_down_sample(2*voxel_size)

        # it was observed that running the outlier removal multiple times improves the skeleton in the case of tree point clouds
        downsampled_skeleton = downsampled_skeleton.remove_statistical_outlier(nb_neighbors=50, std_ratio = 1.5)[0]
        downsampled_skeleton = downsampled_skeleton.remove_statistical_outlier(nb_neighbors=50, std_ratio = 1.5)[0]
        downsampled_skeleton = downsampled_skeleton.remove_statistical_outlier(nb_neighbors=50, std_ratio = 1.5)[0]

        for point in downsampled_skeleton.points:
            skeleton_as_list.append([point[0], 
                                     point[1], 
                                     point[2]])

        self.tree_skeleton = skeleton_as_list

        print("Skeleton computed, n° points = ", len(self.tree_skeleton))
        return self.tree_skeleton

    def __str__(self):
        return f"Tree {self.tree_id} - {self.tree_name}"