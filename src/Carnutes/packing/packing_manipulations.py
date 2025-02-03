"""
This module contains the tree manipulation code for tree combinatorics.
"""

import os
import copy

import utils.database_reader as db_reader
import utils.geometry
import utils.geometrical_operations
import utils.tree

import open3d as o3d
import numpy as np


def match_skeletons(
    model_element: utils.geometry.Pointcloud,
    original_skeleton: utils.geometry.Pointcloud,
) -> utils.geometry.Pointcloud:
    """
    match the two skeletons by adapting the target skeleton to the reference skeleton,
    so the distances between the corresponding points are identical.
    The number of points in the target_skeleton is thus matched to the number of points in the reference_skeleton.

    :param model_element: Pointcloud
        The model element that gives the relative distances between the points

    :param original_skeleton: Pointcloud
        The original tree skeleton to modify so it matches the reference skeleton

    :return: adapted_skeleton: Pointcloud
        The adapted target skeleton
    :return: number_of_segments: int
        The number of segments in the original skeleton that are mithin the length of the model element

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
    for i in range(len(model_element.points) - 1):
        dist = np.linalg.norm(
            np.array(model_element.points[i]) - np.array(model_element.points[i + 1])
        )
        list_of_reference_distances.append(dist)
    list_of_target_distances = []
    for i in range(len(original_skeleton.points) - 1):
        dist = np.linalg.norm(
            np.array(original_skeleton.points[i])
            - np.array(original_skeleton.points[i + 1])
        )
        list_of_target_distances.append(dist)
    new_skeleton_as_list = [
        [
            original_skeleton.points[0][0],
            original_skeleton.points[0][1],
            original_skeleton.points[0][2],
        ]
    ]

    if np.sum(list_of_target_distances) < np.sum(list_of_reference_distances):
        return None, None

    else:
        for i in range(len(list_of_reference_distances)):
            reference_cummulative_distance = np.sum(
                list_of_reference_distances[: i + 1]
            )
            for j in range(len(list_of_target_distances)):
                target_cummulative_distance = np.sum(list_of_target_distances[: j + 1])
                if reference_cummulative_distance < target_cummulative_distance:
                    break
            ratio = (
                np.sum(list_of_reference_distances[: i + 1])
                - np.sum(list_of_target_distances[:j])
            ) / list_of_target_distances[j]
            new_point = [
                original_skeleton.points[j][0]
                + ratio
                * (original_skeleton.points[j + 1][0] - original_skeleton.points[j][0]),
                original_skeleton.points[j][1]
                + ratio
                * (original_skeleton.points[j + 1][1] - original_skeleton.points[j][1]),
                original_skeleton.points[j][2]
                + ratio
                * (original_skeleton.points[j + 1][2] - original_skeleton.points[j][2]),
            ]
            new_skeleton_as_list.append(new_point)
        adapted_skeleton = utils.geometry.Pointcloud(new_skeleton_as_list)
        return adapted_skeleton, j


def perform_icp_registration(
    target_skeleton: utils.geometry.Pointcloud,
    source_skeleton: utils.geometry.Pointcloud,
    max_correspondence_distance: float,
) -> o3d.pipelines.registration.RegistrationResult:
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
    :return: initial_rotation: np.array
        The initial rotation matrix used for the icp registration. It aligns the skeleton to the reference once both have been re-located to the origin.
    """
    source_pc = o3d.geometry.PointCloud()
    source_pc.points = o3d.utility.Vector3dVector(np.array(source_skeleton.points))
    source_pc.estimate_normals()

    target_pc = o3d.geometry.PointCloud()
    target_pc.points = o3d.utility.Vector3dVector(np.array(target_skeleton.points))
    target_pc.estimate_normals()

    # translation to origin
    source_pc.translate(-source_pc.points[0])
    target_pc.translate(-target_pc.points[0])

    # initial rotation
    initial_rotation = (
        utils.geometrical_operations.find_rotation_matrix_between_skeletons(
            target_pc, source_pc
        )
    )

    convergence_criteria = o3d.pipelines.registration.ICPConvergenceCriteria(
        max_iteration=5,
        relative_rmse=1e-6,
    )

    result = o3d.pipelines.registration.registration_icp(
        source=source_pc,
        target=target_pc,
        max_correspondence_distance=max_correspondence_distance,
        init=initial_rotation,
        criteria=convergence_criteria,
    )
    return result, result.transformation
