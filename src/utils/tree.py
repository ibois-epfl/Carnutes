"""
Module storing the Tree class and the geometry classes
"""
#! python3

import persistent
from collections import defaultdict
import copy

from utils.geometry import Pointcloud, Mesh

import numpy as np

import open3d as o3d
from open3d import pipelines
# from pc_skeletor import *
# from pc_skeletor import LBC


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

        self.skeleton = Pointcloud(skeleton_as_list)

        print("Skeleton computed, n° points = ", len(self.skeleton.points))
        return self.skeleton

    def align_to_skeleton(self, reference_skeleton):
        """
        Align the tree to a reference skeleton using ICP
        :param reference_skeleton: Pointcloud
            The reference skeleton to align to
        """
        tree_pc = o3d.geometry.PointCloud()
        tree_pc.points = o3d.utility.Vector3dVector(np.array(self.point_cloud.points))
        skeleton_pc = o3d.geometry.PointCloud()
        skeleton_pc.points = o3d.utility.Vector3dVector(np.array(self.skeleton.points))
        skeleton_pc.estimate_normals()
        reference_pc = o3d.geometry.PointCloud()
        reference_pc.points = o3d.utility.Vector3dVector(np.array(reference_skeleton.points))
        reference_pc.estimate_normals()

        initial_translation = np.identity(4)
        initial_translation[:3, 3] =  np.mean(np.asarray(reference_pc.points), axis=0) - np.mean(np.asarray(tree_pc.points), axis=0)
        tree_pc.transform(initial_translation)
        
        result = o3d.pipelines.registration.registration_icp(skeleton_pc, 
                                                             reference_pc,
                                                             100.0,
                                                             initial_translation)

        transformation = result.transformation
        tree_pc = copy.deepcopy(tree_pc)

        # Assuming an affine transformation
        rotation = transformation[:3, :3]
        translation = transformation[:3, 3]

        new_pointcloud = []
        new_skeleton = []

        for point in self.point_cloud.points:
            point = np.dot(rotation, point) + translation
            new_pointcloud.append(point)

        self.point_cloud = Pointcloud(new_pointcloud, self.point_cloud.colors)

        for point in self.skeleton.points:
            point = np.dot(rotation, point) + translation
            new_skeleton.append(point)
        
        self.skeleton = Pointcloud(new_skeleton)

    def create_mesh(self, radius = 0.25):
        """
        Create a mesh from the point cloud and adds it to the tree instance

        :param radius: float, optional. The radius of the ball pivoting algorithm. The default is 0.25.
        """
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(self.point_cloud.points)
        pcd.estimate_normals()
        # mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(pcd, o3d.utility.DoubleVector([radius, radius * 2]))
        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd, 2)
        mesh.compute_vertex_normals()
        mesh.compute_triangle_normals()
        
        vertices = np.asarray(mesh.vertices)
        faces = np.asarray(mesh.triangles)
        self.mesh = Mesh(vertices, faces)

        print("Mesh created, n° vertices = ", len(self.mesh.vertices), "n° faces = ", len(self.mesh.faces))

    def crop(self, bounding_box):
        """
        Crop the tree to a bounding box
        :param bounding_box: BoundingBox
            The bounding box to crop the tree to
        """
        indexes_to_remove = []
        for i in range(len(self.point_cloud.points)):
            point = self.point_cloud.points[i]
            if not bounding_box.Contains(Rhino.Geometry.Point3d(point[0], point[1], point[2])):
                indexes_to_remove.append(i)
        self.point_cloud.points = [point for i, point in enumerate(self.point_cloud.points) if i not in indexes_to_remove]
        self.point_cloud.colors = [color for i, color in enumerate(self.point_cloud.colors) if i not in indexes_to_remove]

    def __str__(self):
        return f"Tree {self.id} - {self.name}"