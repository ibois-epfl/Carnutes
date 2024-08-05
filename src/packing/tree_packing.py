"""
This module contains the packing code for tree matching
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
      \               |              |
       p              |              p
       |              p              |
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
    print("list of reference distances", list_of_reference_distances)
    list_of_target_distances = []
    for i in range(len(target_skeleton.points)-1):
        dist = np.linalg.norm(np.array(target_skeleton.points[i]) - np.array(target_skeleton.points[i+1]))
        list_of_target_distances.append(dist)
    new_target_skeleton = [[target_skeleton.points[0][0],
                           target_skeleton.points[0][1],
                           target_skeleton.points[0][2]]]

    if np.sum(list_of_target_distances) < np.sum(list_of_reference_distances):
        print("The target skeleton is too short to be adapted to the reference skeleton, returning None")
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
        print("The target skeleton has been adapted to the reference skeleton", new_target_skeleton)
        print("length of the new_target_skeleton is ", len(new_target_skeleton))
        print("length of the target skeleton is ", len(target_skeleton.points))
        return utils.geometry.Pointcloud(new_target_skeleton)

def perform_icp_registration(target_skeleton, source_skeleton, threshold):
    """
    Perform an icp registration between the source and the target pointclouds
    :param target_skeleton: Pointcloud
        The target skeleton to align to
    :param source_skeleton: Pointcloud
        The source skeleton to align
    :param threshold: float
        The threshold for the icp registration
    
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
    initial_translation[:3, 3] = np.mean(np.asarray(target_pc.points), axis=0) - np.mean(np.asarray(source_pc.points), axis=0)

    result = o3d.pipelines.registration.registration_icp(source_pc,
                                                         target_pc,
                                                         threshold,
                                                         initial_translation)
    return result

def find_best_tree(reference_skeleton, reference_diameter, database_path):
    """
    performs icp registrations bewteen the reference skeleton and the list of targets,
    while checking that the diameter is within 10% of the reference value. The skeleton with the best fit is returned.
    The database is updated by removing from it the part of the best fitting skeleton.

    :param reference_skeleton: Pointcloud
        The reference skeleton to align to
    :param reference_diameter: float
        The diameter of the reference skeleton
    :param database_path: str
        The path to the database. The database is updated by removing from it the part of the best fitting skeleton.

    :return: best_tree: Tree
        The best fitting tree for which the skeleton was cropped to the best fitting segment
    """
    # unpack the database:
    reader = db_reader.DatabaseReader(database_path)
    n_tree = reader.get_num_trees()
    best_tree = None
    best_score = np.inf
    # iterate over the trees in the database
    for i in range(n_tree):
        tree = copy.deepcopy(reader.get_tree(i))

        for j in range(2):
            tree.skeleton.points = tree.skeleton.points[::-1] if j % 2 == 1 else tree.skeleton.points
            for k in range(2):
                reference_skeleton.points = reference_skeleton.points[::-1] if k % 2 == 1 else reference_skeleton.points
                tree_skeleton_corresponding_points = match_skeletons(reference_skeleton, tree.skeleton)
                if tree_skeleton_corresponding_points is not None:
                    result = perform_icp_registration(reference_skeleton, tree_skeleton_corresponding_points, 100.0)
                    if result.fitness < best_score:
                        best_score = result.fitness
                        best_tree = tree
                        best_tree.skeleton = tree_skeleton_corresponding_points # update the tree skeleton
                else:
                    pass
    reader.close()
    return best_tree