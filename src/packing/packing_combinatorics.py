"""
This module contains the code for tree combinatorics.
"""

import os
import copy
from typing import List, Tuple
import transaction

import utils.database_reader as db_reader
import utils.geometry
import utils.tree
from . import packing_manipulations

import open3d as o3d
import numpy as np

def compute_best_tree_element_matching(reference: utils.geometry.Pointcloud, target: utils.geometry.Pointcloud, minimum_rmse: float) -> Tuple[utils.geometry.Pointcloud, utils.geometry.Pointcloud]:
    """
    Compute the best matching between the reference and the target point clouds.
    The target point cloud is cropped to the best fitting segment.

    ```	
    ref:           target:      four possible adapted_target:
        p1               p              p1  p3      p3  p1
         \               |              |   |      /   /
          p2             |              p2  p2    p2  p2
          |              p              |   |    /   /
          p3            /               p3  p1  p1  p3
                       /
                      /
                     p
    ```
    :param reference: Pointcloud
        The reference point cloud to align to
    :param target: Pointcloud
        The target point cloud to align
    :param minimum_rmse: float
        The minimum rmse to consider the alignment as valid

    :return: best_reference: Pointcloud
        The best fitting segment of the reference point cloud
    :return: best_target: Pointcloud
        The best fitting segment of the target point cloud
    :return: best_rmse: float
        The rmse of the best fitting segment
    """
    best_rmse = minimum_rmse
    best_reference = None
    best_target = None
    for i in range(2):
        reference.points = reference.points[::-1] if i % 2 == 1 else reference.points
        for j in range(2):
            target.points = target.points[::-1] if j % 2 == 1 else target.points
            print(target.points)
            result = packing_manipulations.perform_icp_registration(reference, target, 20.0)
            if result.inlier_rmse < best_rmse:
                best_rmse = result.inlier_rmse
                best_reference = reference
                best_target = target
    return best_reference, best_target, best_rmse

def find_best_tree(reference_skeleton: utils.geometry.Pointcloud, reference_diameter: float, database_path : str, return_rmse : bool = False) -> Tuple[utils.tree.Tree, float]:
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
    :param return_rmse: bool
        Whether to return the rmse of the best fitting tree. This is for evaluation purposes.

    :return: best_tree: Tree
        The best fitting tree for which the skeleton was cropped to the best fitting segment
    :return: best_reference: Pointcloud
        The best fitting segment of the reference point cloud. Only returned if return_rmse is True.
    :return: best_target: Pointcloud
        The best fitting segment of the target point cloud. Only returned if return_rmse is True.
    :return: rmse: float
        The rmse of the best fitting tree. Only returned if return_rmse is True.
    """
    # unpack the database:
    reader = db_reader.DatabaseReader(database_path)
    n_tree = reader.get_num_trees()
    best_tree = None
    # initiallize the best rmse to infinity before the first iteration
    best_db_level_rmse = np.inf 
    # iterate over the trees in the database
    for i in range(n_tree):
        tree = copy.deepcopy(reader.get_tree(i))
        reference, target, best_tree_level_rmse = compute_best_tree_element_matching(reference_skeleton, tree.skeleton, np.inf)
        if best_tree_level_rmse < best_db_level_rmse:
            best_tree_id = i
            best_db_level_rmse = best_tree_level_rmse
            best_tree = tree
            best_tree.skeleton = target
            best_reference = reference
            best_target = target
    # remove the best tree from the database
    trimmed_tree = packing_manipulations.trim_tree(best_tree, best_target)
    reader.root.trees[best_tree_id] = trimmed_tree
    transaction.commit()

    # close the database
    reader.close()
    if return_rmse:
        return best_tree, best_reference, best_target, best_db_level_rmse
    return best_tree

def tree_based_iterative_matching(reference_skeletons: List[utils.geometry.Pointcloud], database_path: str):
    """
    Iterating tree per tree, we find the best reference skeleton (element in the model) that matches the tree skeleton.

    :param reference_skeletons: List[Pointcloud]
        The list of reference skeletons to match to
    :param database_path: str
        The path to the database. The database is updated by removing from it the part of the best fitting skeleton.

    :return: best_tree_parts: List[Tree]
        The list of best fitting tree parts, in the same order as the reference_skeletons.
    """
    pass

def element_based_iterative_matching(reference_skeletons: List[utils.geometry.Pointcloud], database_path: str):
    """
    Iterating element per element, we find the best tree in the database that matches the reference skeleton (element in the model).
    """
    pass

def combinatorics_matching():
    """
    Smart matching of elements and trees.
    The method is still TBD.
    """
    pass
