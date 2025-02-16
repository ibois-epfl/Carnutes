"""
Module storing the Tree class and the geometry classes
"""

#! python3

import persistent
from collections import defaultdict
import copy

from utils.geometry import Pointcloud, Mesh
from utils.geometrical_operations import *
import utils.meshing as meshing

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

    def __init__(
        self, id: int, name: str, point_cloud: Pointcloud, skeleton: Pointcloud = None
    ):
        self.id = id
        self.name = name
        self.point_cloud = point_cloud
        self.skeleton = skeleton
        self.mean_diameter = None
        self.height = None

    def _p_resolveConflict(self, oldState, savedState, newState):
        """
        Resolve conflicts when saving the object
        """
        savedDiff = savedState["point_cloud"] - oldState["point_cloud"]
        newDiff = newState["point_cloud"] - oldState["point_cloud"]

        if savedDiff == newDiff:
            return newState
        else:
            return oldState  # testing this one out

    def compute_skeleton(self):
        """
        Compute the skeleton of the point cloud .
        For now it is done in a rather sloppy way. this is because pc_skeletor is currently causing issues

        To Do: make this actually professional
        """
        skeleton_points_as_list = []
        skeleton_circles_as_list = []  # list of tuples (center, radius)

        o3d_pc = o3d.geometry.PointCloud()
        o3d_pc.points = o3d.utility.Vector3dVector(self.point_cloud.points)

        oriented_bounding_box = o3d_pc.get_oriented_bounding_box()
        min_bound = oriented_bounding_box.get_min_bound()[2]
        pc_height = oriented_bounding_box.get_max_bound()[2] - min_bound
        self.height = pc_height

        segments = defaultdict(list)
        for point in np.asarray(o3d_pc.points):
            relative_height = point[2] - min_bound
            # We create 10 indexes along the height of the point cloud (we assume the tree upwards)
            index = int(round((SKELETON_LENGTH - 1) * relative_height / pc_height))
            if index not in segments:
                segments[index] = [point]
            else:
                segments[index].append(point)

        for i in range(SKELETON_LENGTH):
            # We compute the center of the segment
            i_th_segment = segments[i]
            center_point = i_th_segment[0]
            for j in range(len(i_th_segment) - 1):
                center_point += i_th_segment[j + 1]
            center_point /= len(i_th_segment)
            skeleton_points_as_list.append(center_point)

            # We project the segment to the plane defined by the center point and the z axis as normal
            i_th_projected_points = project_points_to_plane(
                i_th_segment, center_point, [0, 0, 1]
            )

            # We fit a circle to the projected points
            i_th_circle_parameters = fit_circle_with_open3d(
                i_th_projected_points,
                distance_threshold=0.01,
                ransac_n=3,
                num_iterations=1000,
            )
            skeleton_circles_as_list.append(i_th_circle_parameters)

        self.skeleton = Pointcloud(skeleton_points_as_list)
        self.skeleton_circles = skeleton_circles_as_list
        self.mean_diameter = np.mean(
            [2 * circle[1] for circle in skeleton_circles_as_list]
        )

        return self.skeleton

    def align_to_skeleton(self, reference_skeleton, initial_rotation=None):
        """
        Align the tree to a reference skeleton using ICP
        :param reference_skeleton: Pointcloud
            The reference skeleton to align to
        :param initial_rotation: np.array (4,4), optional
            The initial rotation matrix to use for the ICP registration. None by default.
        """
        tree_pc = o3d.geometry.PointCloud()
        tree_pc.points = o3d.utility.Vector3dVector(np.array(self.point_cloud.points))
        skeleton_pc = o3d.geometry.PointCloud()
        skeleton_pc.points = o3d.utility.Vector3dVector(np.array(self.skeleton.points))
        skeleton_pc.estimate_normals()
        reference_pc = o3d.geometry.PointCloud()
        reference_pc.points = o3d.utility.Vector3dVector(
            np.array(reference_skeleton.points)
        )
        reference_pc.estimate_normals()

        t_origin_to_reference = np.eye(4)
        t_origin_to_reference[0, 3] = reference_pc.points[0][0]
        t_origin_to_reference[1, 3] = reference_pc.points[0][1]
        t_origin_to_reference[2, 3] = reference_pc.points[0][2]

        t_skeleton_to_origin = np.eye(4)
        t_skeleton_to_origin[0, 3] = -skeleton_pc.points[0][0]
        t_skeleton_to_origin[1, 3] = -skeleton_pc.points[0][1]
        t_skeleton_to_origin[2, 3] = -skeleton_pc.points[0][2]

        tree_pc.translate(-skeleton_pc.points[0])
        skeleton_pc.translate(-skeleton_pc.points[0])
        reference_pc.translate(-reference_pc.points[0])

        initial_rotation = find_rotation_matrix_between_skeletons(
            reference_pc, skeleton_pc
        )

        convergence_criteria = o3d.pipelines.registration.ICPConvergenceCriteria(
            max_iteration=5, relative_rmse=1.000000e-06
        )

        result = o3d.pipelines.registration.registration_icp(
            source=skeleton_pc,
            target=reference_pc,
            init=initial_rotation,
            max_correspondence_distance=20.0,
            criteria=convergence_criteria,
        )
        print(
            f"rmse is {result.inlier_rmse}  and fitness is {result.fitness} after latest icp in tree.py, align skeletons of {len(skeleton_pc.points)} and {len(reference_pc.points)} points"
        )
        transformation = np.dot(
            t_origin_to_reference, np.dot(result.transformation, t_skeleton_to_origin)
        )
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

    def create_mesh(self, alpha=2):
        """
        Create a mesh from the point cloud and adds it to the tree instance

        :param radius: float, optional. The radius of the ball pivoting algorithm. The default is 0.25.
        """
        self.mesh = meshing.mesh_from_tree_pointcloud(
            self.point_cloud, meshing.MeshingMethod.ALPHA, alpha=alpha
        )

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
        x_max_bounds += 0.1 * delta_x
        x_min_bounds -= 0.1 * delta_x
        y_max_bounds = max([point[1] for point in skeleton_to_remove.points])
        y_min_bounds = min([point[1] for point in skeleton_to_remove.points])
        delta_y = y_max_bounds - y_min_bounds
        y_max_bounds += 0.1 * delta_y
        y_min_bounds -= 0.1 * delta_y
        z_max_bounds = max([point[2] for point in skeleton_to_remove.points])
        z_min_bounds = min([point[2] for point in skeleton_to_remove.points])
        delta_z = z_max_bounds - z_min_bounds
        z_max_bounds += 0.1 * delta_z
        z_min_bounds -= 0.1 * delta_z
        new_skeleton = []
        new_points = []
        new_colors = []
        new_circles = []
        if delta_x > delta_y and delta_x > delta_z:  # meaning that the main axis is x
            for i, point in enumerate(self.point_cloud.points):
                if point[0] < x_min_bounds or x_max_bounds < point[0]:
                    new_points.append(point)
                    new_colors.append(self.point_cloud.colors[i])
            for point in self.skeleton.points:
                if point[0] < x_min_bounds or x_max_bounds < point[0]:
                    new_skeleton.append(point)
            for circle in self.skeleton_circles:
                if circle[0][0] < x_min_bounds or x_max_bounds < circle[0][0]:
                    new_circles.append(circle)
        elif delta_y > delta_x and delta_y > delta_z:  # meaning that the main axis is y
            for i, point in enumerate(self.point_cloud.points):
                if point[1] < y_min_bounds or y_max_bounds < point[1]:
                    new_points.append(point)
                    new_colors.append(self.point_cloud.colors[i])
            for point in self.skeleton.points:
                if point[1] < y_min_bounds or y_max_bounds < point[1]:
                    new_skeleton.append(point)
            for circle in self.skeleton_circles:
                if circle[0][1] < y_min_bounds or y_max_bounds < circle[0][1]:
                    new_circles.append(circle)
        elif delta_z > delta_x and delta_z > delta_y:  # meaning that the main axis is z
            for i, point in enumerate(self.point_cloud.points):
                if point[2] < z_min_bounds or z_max_bounds < point[2]:
                    new_points.append(point)
                    new_colors.append(self.point_cloud.colors[i])
            for point in self.skeleton.points:
                if point[2] < z_min_bounds or z_max_bounds < point[2]:
                    new_skeleton.append(point)
            for circle in self.skeleton_circles:
                if circle[0][2] < z_min_bounds or z_max_bounds < circle[0][2]:
                    new_circles.append(circle)
        self.point_cloud.points = new_points
        self.point_cloud.colors = new_colors
        self.skeleton.points = new_skeleton
        self.skeleton_circles = new_circles

        if len(self.point_cloud.points) > 1:
            self.height = max([point[2] for point in self.point_cloud.points]) - min(
                [point[2] for point in self.point_cloud.points]
            )

    def __str__(self):
        return f"Tree {self.id} - {self.name}"
