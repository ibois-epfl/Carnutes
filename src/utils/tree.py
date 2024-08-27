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

# from pc_skeletor import *
# from pc_skeletor import LBC

print("version of numpy is ", np.__version__)

# The number of points of the tree skeleton
SKELETON_LENGTH = 11

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

    def _p_resolveConflict(self, oldState, savedState, newState):
        """
        Resolve conflicts when saving the object
        """
        savedDiff = savedState['point_cloud'] - oldState['point_cloud']
        newDiff = newState['point_cloud'] - oldState['point_cloud']

        if savedDiff == newDiff:
            return newState
        else:
            return oldState # testing this one out

    def compute_skeleton(self):
        """
        Compute the skeleton of the point cloud .
        For now it is done in a rather sloppy way. this is because pc_skeletor is currently causing issues

        To Do: make this actually professional
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
        for i in range(SKELETON_LENGTH):
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
        print("Skeleton points are ", self.skeleton.points)
        skeleton_pc.points = o3d.utility.Vector3dVector(np.array(self.skeleton.points))
        skeleton_pc.estimate_normals()
        reference_pc = o3d.geometry.PointCloud()
        reference_pc.points = o3d.utility.Vector3dVector(np.array(reference_skeleton.points))

        print("Aligning tree to skeleton using as reference: ", reference_pc, "with points:")
        all_points_ref = np.asarray(reference_pc.points)
        for i in range(len(all_points_ref)):
            print(np.asarray(all_points_ref[i]))
        print("And using as skeleton: ", skeleton_pc, "with points:")
        all_points_skel = np.asarray(skeleton_pc.points)
        for i in range(len(all_points_skel)):
            print(np.asarray(all_points_skel[i]))

        initial_translation = np.identity(4)
        initial_translation[:3, 3] =  np.mean(np.asarray(reference_pc.points), axis=0) - np.mean(np.asarray(skeleton_pc.points), axis=0)
        tree_pc.transform(initial_translation)

        convergence_criteria = o3d.pipelines.registration.ICPConvergenceCriteria(relative_fitness=1.000000e-03, 
                                                                                 max_iteration = 40,
                                                                                 relative_rmse=1.000000e-03)
        
        result = o3d.pipelines.registration.registration_icp(source=skeleton_pc, 
                                                             target=reference_pc,
                                                             init=initial_translation,
                                                             max_correspondence_distance=10.0,
                                                             criteria=convergence_criteria)

        transformation = result.transformation
        print("Transformation matrix is ", transformation)
        tree_pc = copy.deepcopy(tree_pc)

        # Assuming an affine transformation
        rotation = transformation[:3, :3]
        translation = transformation[:3, 3]

        new_pointcloud_as_list = []
        new_colors_as_list = self.point_cloud.colors
        new_skeleton_as_list = []

        for point in self.point_cloud.points:
            point = np.dot(rotation, point) + translation
            new_pointcloud_as_list.append([point[0], point[1], point[2]])

        self.point_cloud = Pointcloud(new_pointcloud_as_list, new_colors_as_list)

        for point in self.skeleton.points:
            point = np.dot(rotation, point) + translation
            new_skeleton_as_list.append([point[0], point[1], point[2]])
        
        self.skeleton = Pointcloud(new_skeleton_as_list)

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
        colors = np.asarray(mesh.vertex_colors)
        self.mesh = Mesh(vertices, faces, colors)

        print("Mesh created, n° vertices = ", len(self.mesh.vertices), "n° faces = ", len(self.mesh.faces))

    def trim(self, skeleton_to_remove):
        """
        Trim the tree by removing all the that are within the range of the skeleton_to_remove
        :param skeleton_to_remove: Pointcloud
            The skeleton to remove
        """
        # First indicate that the object has been changed
        self._p_changed = 1

        # Then remove the points that are within the range of the skeleton_to_remove, with a 10% margin of safety:
        x_max_bounds = max([point[0] for point in skeleton_to_remove.points])
        x_min_bounds = min([point[0] for point in skeleton_to_remove.points])
        delta_x = x_max_bounds - x_min_bounds
        x_max_bounds += 0.1*delta_x
        x_min_bounds -= 0.1*delta_x
        y_max_bounds = max([point[1] for point in skeleton_to_remove.points])
        y_min_bounds = min([point[1] for point in skeleton_to_remove.points])
        delta_y = y_max_bounds - y_min_bounds
        y_max_bounds += 0.1*delta_y
        y_min_bounds -= 0.1*delta_y
        z_max_bounds = max([point[2] for point in skeleton_to_remove.points])
        z_min_bounds = min([point[2] for point in skeleton_to_remove.points])
        delta_z = z_max_bounds - z_min_bounds
        z_max_bounds += 0.1*delta_z
        z_min_bounds -= 0.1*delta_z
        new_skeleton = []
        new_points = []
        new_colors = []
        if delta_x > delta_y and delta_x > delta_z: # meaning that the main axis is x
            for i, point in enumerate(self.point_cloud.points):
                if point[0] < x_min_bounds or x_max_bounds < point[0]:
                    new_points.append(point)
                    new_colors.append(self.point_cloud.colors[i])
            for point in self.skeleton.points:
                if point[0] < x_min_bounds or x_max_bounds < point[0]:
                    new_skeleton.append(point)
        elif delta_y > delta_x and delta_y > delta_z: # meaning that the main axis is y
            for i, point in enumerate(self.point_cloud.points):
                if point[1] < y_min_bounds or y_max_bounds < point[1]:
                    new_points.append(point)
                    new_colors.append(self.point_cloud.colors[i])
            for point in self.skeleton.points:
                if point[1] < y_min_bounds or y_max_bounds < point[1]:
                    new_skeleton.append(point)
        elif delta_z > delta_x and delta_z > delta_y: # meaning that the main axis is z
            for i, point in enumerate(self.point_cloud.points):
                if point[2] < z_min_bounds or z_max_bounds < point[2]:
                    new_points.append(point)
                    new_colors.append(self.point_cloud.colors[i])
            for point in self.skeleton.points:
                if point[2] < z_min_bounds or z_max_bounds < point[2]:
                    new_skeleton.append(point)
        self.point_cloud.points = new_points
        self.point_cloud.colors = new_colors
        self.skeleton.points = new_skeleton

    def __str__(self):
        return f"Tree {self.id} - {self.name}"