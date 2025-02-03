"""
This module contains the various geometrical operations that are perfornmed thoughout the code
"""

import typing

import numpy as np
import open3d as o3d


def project_points_to_plane(
    points: typing.List[typing.List[float]],
    plane_origin: typing.List[float],
    plane_normal: typing.List[float],
) -> typing.List[typing.List[float]]:
    """
    Project a list of points to a plane.

    :param points: list of list of float
        List of points to project.
    :param plane: list of float
        The plane to project the points to.

    :return: list of list of float
        The projected points.
    """
    # Just checking the normal is a unit vector
    plane_normal = np.array(plane_normal)
    plane_normal = plane_normal / np.linalg.norm(plane_normal)

    projected_points = []
    for point in points:
        point_to_origin_vector = np.array(point) - np.array(plane_origin)
        projection_along_normal = np.dot(point_to_origin_vector, plane_normal)
        projection_vector = projection_along_normal * plane_normal
        projected_point = np.array(point) - projection_vector
        point = projected_point.tolist()
        projected_points.append(point)

    return projected_points


def fit_circle_with_open3d(
    points, distance_threshold=0.01, ransac_n=3, num_iterations=1000
):
    # Convert points to Open3D PointCloud
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(points)

    # Fit a plane to the point cloud
    plane_model, inliers = point_cloud.segment_plane(
        distance_threshold=distance_threshold,
        ransac_n=ransac_n,
        num_iterations=num_iterations,
    )

    # Extract inlier points
    inlier_cloud = point_cloud.select_by_index(inliers)

    # Convert inlier points to numpy array
    inlier_points = np.asarray(inlier_cloud.points)

    # Fit a circle to the inlier points
    # Assuming the points are approximately in a plane, we can project them to 2D
    centroid = np.mean(inlier_points, axis=0)
    centered_points = inlier_points - centroid
    u, s, vh = np.linalg.svd(centered_points)
    normal = vh[2, :]
    projected_points = centered_points - np.outer(
        np.dot(centered_points, normal), normal
    )

    # Fit a circle in 2D
    A = np.hstack(
        [2 * projected_points[:, :2], np.ones((projected_points.shape[0], 1))]
    )
    b = np.sum(projected_points[:, :2] ** 2, axis=1)
    x = np.linalg.lstsq(A, b, rcond=None)[0]
    center_2d = x[:2]
    radius = np.sqrt(x[2] + np.sum(center_2d**2))

    # Convert the 2D center back to 3D
    center_3d = centroid + center_2d[0] * vh[0, :3] + center_2d[1] * vh[1, :3]

    return center_3d, radius


def find_rotation_matrix_between_skeletons(first_skeleton, second_skeleton) -> int:
    """
    Find the rotation angle between two skeletons

    :param first_skeleton: Pointcloud
        The first skeleton
    :param second_skeleton: Pointcloud
        The second skeleton

    :return: rotation matrix
        The 4x4 rotation matrix from the first to the second skeleton
    """
    rotation_matrix = np.identity(4)

    vector_for_angle_calculation_1 = np.array(first_skeleton.points[-1]) - np.array(
        first_skeleton.points[0]
    )
    vector_for_angle_calculation_2 = np.array(second_skeleton.points[-1]) - np.array(
        second_skeleton.points[0]
    )
    angle = -np.arccos(
        np.dot(vector_for_angle_calculation_1, vector_for_angle_calculation_2)
        / (
            np.linalg.norm(vector_for_angle_calculation_1)
            * np.linalg.norm(vector_for_angle_calculation_2)
        )
    )

    rotation_axis = np.cross(
        vector_for_angle_calculation_1, vector_for_angle_calculation_2
    )
    rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)

    # https://en.wikipedia.org/wiki/Rotation_matrix#Rotation_matrix_from_axis_and_angle
    rotation_matrix[0, 0] = rotation_axis[0] ** 2 * (1 - np.cos(angle)) + np.cos(angle)
    rotation_matrix[0, 1] = rotation_axis[0] * rotation_axis[1] * (
        1 - np.cos(angle)
    ) - rotation_axis[2] * np.sin(angle)
    rotation_matrix[0, 2] = rotation_axis[0] * rotation_axis[2] * (
        1 - np.cos(angle)
    ) + rotation_axis[1] * np.sin(angle)
    rotation_matrix[1, 0] = rotation_axis[1] * rotation_axis[0] * (
        1 - np.cos(angle)
    ) + rotation_axis[2] * np.sin(angle)
    rotation_matrix[1, 1] = rotation_axis[1] ** 2 * (1 - np.cos(angle)) + np.cos(angle)
    rotation_matrix[1, 2] = rotation_axis[1] * rotation_axis[2] * (
        1 - np.cos(angle)
    ) - rotation_axis[0] * np.sin(angle)
    rotation_matrix[2, 0] = rotation_axis[2] * rotation_axis[0] * (
        1 - np.cos(angle)
    ) - rotation_axis[1] * np.sin(angle)
    rotation_matrix[2, 1] = rotation_axis[2] * rotation_axis[1] * (
        1 - np.cos(angle)
    ) + rotation_axis[0] * np.sin(angle)
    rotation_matrix[2, 2] = rotation_axis[2] ** 2 * (1 - np.cos(angle)) + np.cos(angle)

    return rotation_matrix
