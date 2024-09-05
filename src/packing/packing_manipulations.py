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


def match_skeletons(
    model_element: utils.geometry.Pointcloud,
    original_skeleton: utils.geometry.Pointcloud,
) -> utils.geometry.Pointcloud:
    """ "
    match the two skeletons by adapting the target skeleton to the reference skeleton,
    so the distances between the corresponding points are identical.
    The number of points in the target_skeleton is thus matched to the number of points in the reference_skeleton.

    :param model_element: Pointcloud
        The model element that gives the relative distances between the points

    :param original_skeleton: Pointcloud
        The original tree skeleton to modify so it matches the reference skeleton

    :return: adapted_skeleton: Pointcloud
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
        return None

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
        return utils.geometry.Pointcloud(new_skeleton_as_list)


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
    """
    source_pc = o3d.geometry.PointCloud()
    source_pc.points = o3d.utility.Vector3dVector(np.array(source_skeleton.points))
    source_pc.estimate_normals()

    target_pc = o3d.geometry.PointCloud()
    target_pc.points = o3d.utility.Vector3dVector(np.array(target_skeleton.points))
    target_pc.estimate_normals()

    # initial translation
    initial_translation = np.identity(4)
    translation_vector = np.mean(target_skeleton.points, axis=0) - np.mean(
        source_skeleton.points, axis=0
    )
    initial_translation[0, 3] = translation_vector[0]
    initial_translation[1, 3] = translation_vector[1]
    initial_translation[2, 3] = translation_vector[2]

    convergence_criteria = o3d.pipelines.registration.ICPConvergenceCriteria(
        max_iteration=40
    )

    result = o3d.pipelines.registration.registration_icp(
        source=source_pc,
        target=target_pc,
        max_correspondence_distance=max_correspondence_distance,
        init=initial_translation,
        criteria=convergence_criteria,
    )
    return result
