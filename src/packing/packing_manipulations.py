"""
This module contains the tree manipulation code for tree combinatorics.
"""
import os
import copy

import utils.database_reader as db_reader
import utils.geometry
import utils.tree

import open3d as o3d
import numpy as np

def match_skeletons(reference_skeleton: utils.geometry.Pointcloud, target_skeleton: utils.geometry.Pointcloud) -> utils.geometry.Pointcloud:
    """"
    match the two skeletons by adapting the target skeleton to the reference skeleton, 
    so the distances between the corresponding points are identical. 
    The number of points in the target_skeleton is thus matched to the number of points in the reference_skeleton.

    :param reference_skeleton: Pointcloud
        The reference skeleton to match to

    :param target_skeleton: Pointcloud
        The target tree skeleton to modify so it matches the reference skeleton

    :return: adapted_target_skeleton: Pointcloud
        The adapted target skeleton
    ```
    ref:           target:      adapted_target:
     p                p              p
      \               or             |
       p              or             p
       or             p              |
       p             /               p
      /             /               /
     /             /               /
    p             p               p
    ```
    """
    list_of_reference_distances = []
    for i in range(len(reference_skeleton.points)-1):
        dist = np.linalg.norm(np.array(reference_skeleton.points[i]) - np.array(reference_skeleton.points[i+1]))
        list_of_reference_distances.append(dist)
    list_of_target_distances = []
    for i in range(len(target_skeleton.points)-1):
        dist = np.linalg.norm(np.array(target_skeleton.points[i]) - np.array(target_skeleton.points[i+1]))
        list_of_target_distances.append(dist)
    new_target_skeleton = [[target_skeleton.points[0][0],
                           target_skeleton.points[0][1],
                           target_skeleton.points[0][2]]]

    if np.sum(list_of_target_distances) < np.sum(list_of_reference_distances):
        return None
        
    else:
        for i in range(len(list_of_reference_distances)):
            reference_cummulative_distance = np.sum(list_of_reference_distances[:i+1])
            for j in range(len(list_of_target_distances)):
                target_cummulative_distance = np.sum(list_of_target_distances[:j+1])
                if reference_cummulative_distance < target_cummulative_distance:
                    break
            ratio = (np.sum(list_of_reference_distances[:i+1]) - np.sum(list_of_target_distances[:j]))/list_of_target_distances[j]
            new_point =  [target_skeleton.points[j][0] + ratio * (target_skeleton.points[j+1][0] - target_skeleton.points[j][0]), 
                          target_skeleton.points[j][1] + ratio * (target_skeleton.points[j+1][1] - target_skeleton.points[j][1]), 
                          target_skeleton.points[j][2] + ratio * (target_skeleton.points[j+1][2] - target_skeleton.points[j][2])]
            new_target_skeleton.append(new_point)
        return utils.geometry.Pointcloud(new_target_skeleton)

def perform_icp_registration(target_skeleton : utils.geometry.Pointcloud, source_skeleton : utils.geometry.Pointcloud, max_correspondence_distance : float) -> o3d.pipelines.registration.RegistrationResult:
    """
    Perform an icp registration between the source and the target pointclouds
    :param target_skeleton: Pointcloud
        The target skeleton to align to
    :param source_skeleton: Pointcloud
        The source skeleton to align
    :param max_correspondence_distance: float
        The max correspondence distance for the icp registration
    
    :return: result: o3d.pipelines.registration.RegistrationResult
        The result of the icp registration
    """
    source_pc = o3d.geometry.PointCloud()
    source_pc.points = o3d.utility.Vector3dVector(np.array(source_skeleton.points))
    source_pc.estimate_normals()

    target_pc = o3d.geometry.PointCloud()
    target_pc.points = o3d.utility.Vector3dVector(np.array(target_skeleton.points))
    target_pc.estimate_normals()

    # initial translation
    initial_translation = np.identity(4)
    translation_vector = np.mean(target_skeleton.points, axis=0) - np.mean(source_skeleton.points, axis=0)
    initial_translation[0, 3] = translation_vector[0]
    initial_translation[1, 3] = translation_vector[1]
    initial_translation[2, 3] = translation_vector[2]

    convergence_criteria = o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration = 40)

    result = o3d.pipelines.registration.registration_icp(source=source_pc,
                                                         target=target_pc,
                                                         max_correspondence_distance=max_correspondence_distance,
                                                         init=initial_translation,
                                                         criteria=convergence_criteria)
    return result

def trim_tree(tree_to_trim : utils.tree.Tree, skeleton : utils.geometry.Pointcloud) -> utils.tree.Tree:
    """
    Trim the tree to the bounding box of the skeleton
    :param tree_to_trim: Tree
        The tree to trim
    :param skeleton: Pointcloud
        The skeleton to trim to
    
    :return: trimmed_tree: Tree
        The trimmed tree
    """
    x_max_bounds = max([point[0] for point in skeleton.points])
    x_min_bounds = min([point[0] for point in skeleton.points])
    delta_x = x_max_bounds - x_min_bounds
    y_max_bounds = max([point[1] for point in skeleton.points])
    y_min_bounds = min([point[1] for point in skeleton.points])
    delta_y = y_max_bounds - y_min_bounds
    z_max_bounds = max([point[2] for point in skeleton.points])
    z_min_bounds = min([point[2] for point in skeleton.points])
    delta_z = z_max_bounds - z_min_bounds
    new_skeleton = []
    new_points = []
    new_colors = []
    if delta_x > delta_y and delta_x > delta_z: # meaning that the main axis is x
        for i, point in enumerate(tree_to_trim.point_cloud.points):
            if point[0] < x_min_bounds or x_max_bounds < point[0]:
                new_points.append(point)
                new_colors.append(tree_to_trim.point_cloud.colors[i])
        for point in tree_to_trim.skeleton.points:
            if point[0] < x_min_bounds or x_max_bounds < point[0]:
                new_skeleton.append(point)
    elif delta_y > delta_x and delta_y > delta_z: # meaning that the main axis is y
        for i, point in enumerate(tree_to_trim.point_cloud.points):
            if point[1] < y_min_bounds or y_max_bounds < point[1]:
                new_points.append(point)
                new_colors.append(tree_to_trim.point_cloud.colors[i])
        for point in tree_to_trim.skeleton.points:
            if point[1] < y_min_bounds or y_max_bounds < point[1]:
                new_skeleton.append(point)
    elif delta_z > delta_x and delta_z > delta_y: # meaning that the main axis is z
        for i, point in enumerate(tree_to_trim.point_cloud.points):
            if point[2] < z_min_bounds or z_max_bounds < point[2]:
                new_points.append(point)
                new_colors.append(tree_to_trim.point_cloud.colors[i])
        for point in tree_to_trim.skeleton.points:
            if point[2] < z_min_bounds or z_max_bounds < point[2]:
                new_skeleton.append(point)
    tree_to_trim.point_cloud.points = new_points
    tree_to_trim.point_cloud.colors = new_colors
    tree_to_trim.skeleton.points = new_skeleton

    return tree_to_trim