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


def compute_best_tree_element_matching(
    model_element: utils.geometry.Pointcloud,
    skeleton: utils.geometry.Pointcloud,
    minimum_rmse: float,
) -> Tuple[utils.geometry.Pointcloud, utils.geometry.Pointcloud]:
    """
    Compute the best matching between the reference and the target point clouds.
    The target point cloud is cropped to the best fitting segment.

    ```
    model element:    skeleton:     four possible skeleton_segments:
        p1               p              p1  p3      p3  p1
         \               |              |   |      /   /
          p2             |              p2  p2    p2  p2
          |              p              |   |    /   /
          p3            /               p3  p1  p1  p3
                       /
                      /
                     p
    ```
    :param model_element: Pointcloud
        The model element point cloud to align to
    :param skeleton: Pointcloud
        The skeleton point cloud to align
    :param minimum_rmse: float
        The minimum rmse to consider the alignment as valid

    :return: best_skeleton: Pointcloud
        The best fitting segment of the skeleton point cloud
    :return: best_rmse: float
        The rmse of the best fitting segment
    """
    best_rmse = minimum_rmse
    best_skeleton = None

    for i in range(2):
        model_element.points = (
            model_element.points[::-1] if i % 2 == 1 else model_element.points
        )
        for j in range(2):
            skeleton.points = skeleton.points[::-1] if j % 2 == 1 else skeleton.points
            adapted_skeleton = packing_manipulations.match_skeletons(
                model_element, skeleton
            )
            if adapted_skeleton is None:
                continue
            result = packing_manipulations.perform_icp_registration(
                model_element, adapted_skeleton, 20.0
            )
            if result.inlier_rmse < best_rmse:
                best_rmse = result.inlier_rmse
                best_skeleton = adapted_skeleton
    if best_rmse is None:
        return None, None
    return best_skeleton, best_rmse


def find_best_tree_unoptimized(
    model_element: utils.geometry.Pointcloud,
    reference_diameter: float,
    database_path: str,
    return_rmse: bool = False,
    update_database: bool = True,
):
    """
    performs icp registrations bewteen the reference skeleton and the list of targets,
    while checking that the diameter is within 10% of the reference value. The skeleton with the best fit is returned.
    Here there is no optimization basd on the lengths of the elements chosen in the database (to choose the shortest elements first).
    The database is updated by removing from it the part of the best fitting skeleton.

    :param reference_skeleton: Pointcloud
        The reference skeleton to align to
    :param reference_diameter: float
        The diameter of the reference skeleton
    :param database_path: str
        The path to the database. The database is updated by removing from it the part of the best fitting skeleton.
    :param return_rmse: bool
        Whether to return the rmse of the best fitting tree. This is for evaluation purposes.
    :param update_database: bool
        Whether to update the database by removing the best fitting tree from it.

    :return: best_tree: Tree
        The best fitting tree for which the skeleton was cropped to the best fitting segment
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
        tree = reader.get_tree(i)
        if tree is not None:
            tree = copy.deepcopy(tree)
        else:
            continue
        if (
            tree.mean_diameter < 0.75 * reference_diameter
            or tree.mean_diameter > 1.25 * reference_diameter
        ):
            continue
        (
            best_skeleton_segment,
            best_tree_level_rmse,
        ) = compute_best_tree_element_matching(model_element, tree.skeleton, np.inf)

        if (
            best_tree_level_rmse is not None
            and best_tree_level_rmse < best_db_level_rmse
        ):
            best_tree_id = i
            best_db_level_rmse = best_tree_level_rmse
            best_tree = tree
            best_skeleton = best_skeleton_segment

        if (
            best_db_level_rmse < 0.01
        ):  # if the RMSE is under 1 cm, we can break the loop
            break

    if best_tree is not None:
        # remove the best tree from the database
        print(
            f"Best tree is {best_tree.id} with rmse {best_db_level_rmse} and height {best_tree.height}"
        )

        selected_tree = copy.deepcopy(best_tree)
        selected_tree.skeleton = best_skeleton
        best_tree.trim(best_skeleton)

        if update_database:
            # remove the tree from the database if its skeleton is a single point, or empty.
            if len(best_tree.skeleton.points) < 2:
                reader.root.trees.pop(best_tree_id)
                reader.root.n_trees -= 1
                transaction.commit()
                reader.close()

            # update the database, as done in https://zodb.org/en/latest/articles/ZODB1.html#a-simple-example
            else:
                trees_in_db = reader.root.trees
                trees_in_db[best_tree_id] = best_tree
                reader.root.trees = trees_in_db
                transaction.commit()
            # close the database
            reader.close()
        if return_rmse:
            return (
                selected_tree,
                best_skeleton_segment,
                best_db_level_rmse,
            )
        return selected_tree
    else:
        reader.close()
        print("No tree found in find_best_tree, returning None")
        return None, None, None


def find_best_tree_optimized(
    model_element: utils.geometry.Pointcloud,
    reference_diameter: float,
    database_path: str,
    optimisation_basis: int,
    return_rmse: bool = False,
    update_database: bool = True,
):
    """
    performs icp registrations bewteen the reference skeleton and the list of targets,
    while checking that the diameter is within 10% of the reference value. The skeleton with the best fit is returned.
    Here there is no optimization basd on the lengths of the elements chosen in the database (to choose the shortest elements first).
    The database is updated by removing from it the part of the best fitting skeleton.

    :param reference_skeleton: Pointcloud
        The reference skeleton to align to
    :param reference_diameter: float
        The diameter of the reference skeleton
    :param database_path: str
        The path to the database. The database is updated by removing from it the part of the best fitting skeleton.
    :param optimisation_basis: int
        The number of elements to consider for the optimisation
    :param return_rmse: bool
        Whether to return the rmse of the best fitting tree. This is for evaluation purposes.
    :param update_database: bool
        Whether to update the database by removing the best fitting tree from it.

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

    rmse = []
    trees = []
    skeleton_segments = []
    tree_ids = []

    # iterate over the trees in the database
    for i in range(n_tree):
        tree = reader.get_tree(i)
        if tree is not None:
            tree = copy.deepcopy(tree)
        else:
            continue
        if (
            tree.mean_diameter < 0.75 * reference_diameter
            or tree.mean_diameter > 1.25 * reference_diameter
        ):
            continue
        (
            best_skeleton_segment,
            best_tree_level_rmse,
        ) = compute_best_tree_element_matching(model_element, tree.skeleton, np.inf)

        if best_tree_level_rmse is not None and best_tree_level_rmse is not np.inf:
            rmse.append(best_tree_level_rmse)
            trees.append(tree)
            skeleton_segments.append(best_skeleton_segment)
            tree_ids.append(i)

    if len(rmse) == 0:
        reader.close()
        print(
            f"No tree were found in the database, but {optimisation_basis} are required"
        )
        return None, None, None
    (sorted_rmse, sorted_trees, sorted_skeleton_segments, sorted_tree_ids,) = zip(
        *sorted(
            zip(rmse, trees, skeleton_segments, tree_ids),
            key=lambda x: rmse,
        )
    )
    n_best_trees = sorted_trees[:optimisation_basis]
    n_best_rmse = sorted_rmse[:optimisation_basis]
    n_best_skeleton = sorted_skeleton_segments[:optimisation_basis]
    n_best_tree_ids = sorted_tree_ids[:optimisation_basis]

    (
        sorted_best_tree,
        sorted_best_db_level_rmse,
        sorted_best_skeleton,
        sorted_best_tree_id,
    ) = zip(
        *sorted(
            zip(n_best_trees, n_best_rmse, n_best_skeleton, n_best_tree_ids),
            key=lambda x: x[0].height,
        )
    )  # get the tree with the smallest height among the five best fitting trees

    best_tree = sorted_best_tree[0]
    best_db_level_rmse = sorted_best_db_level_rmse[0]
    best_skeleton = sorted_best_skeleton[0]
    best_tree_id = sorted_best_tree_id[0]

    if best_tree is not None:
        # remove the best tree from the database
        print(
            f"Best tree is {best_tree.id} with rmse {best_db_level_rmse} and height {best_tree.height}"
        )

        selected_tree = copy.deepcopy(best_tree)
        selected_tree.skeleton = best_skeleton
        best_tree.trim(best_skeleton)

        if update_database:
            # remove the tree from the database if its skeleton is a single point, or empty.
            if len(best_tree.skeleton.points) < 2:
                reader.root.trees.pop(best_tree_id)
                reader.root.n_trees -= 1
                transaction.commit()

            # update the database, as done in https://zodb.org/en/latest/articles/ZODB1.html#a-simple-example
            else:
                trees_in_db = reader.root.trees
                trees_in_db[best_tree_id] = best_tree
                reader.root.trees = trees_in_db
                transaction.commit()

            # close the database
            reader.close()
        if return_rmse:
            return (
                selected_tree,
                best_skeleton_segment,
                best_db_level_rmse,
            )
        reader.close()
        return selected_tree

    else:
        reader.close()
        print("No tree found in find_best_tree, returning None")
        return None, None, None, None


def tree_based_iterative_matching(
    model_elements: List[utils.geometry.Pointcloud], database_path: str
):
    """
    Iterating tree per tree, we find the best reference skeleton (element in the model) that matches the tree skeleton.

    :param model_elements: List[Pointcloud]
        The list of elements to match to
    :param database_path: str
        The path to the database. The database is updated by removing from it the part of the best fitting skeleton.

    :return: best_tree_parts: List[Tree]
        The list of best fitting tree parts, in the same order as the reference_skeletons.
    """
    pass


def element_based_iterative_matching(
    model_elements: List[utils.geometry.Pointcloud], database_path: str
):
    """
    Iterating element per element, we find the best tree in the database that matches the reference model_elements (element in the model).

    :param model_elements: List[Element]
        The list of elements to match to
    """
    list_of_rmse = []
    list_of_best_trees = []
    for model_element in model_elements:
        best_tree, best_reference, best_target, rmse = find_best_tree(
            model_element, 100.0, database_path, return_rmse=True
        )
        list_of_rmse.append(rmse)
        list_of_best_trees.append(best_tree)
    return list_of_best_trees, list_of_rmse


def combinatorics_matching():
    """
    Smart matching of elements and trees.
    The method is still TBD.
    """
    pass
