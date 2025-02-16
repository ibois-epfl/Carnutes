"""
This module contains the meshing utilities
"""

#! python3

import open3d as o3d
import numpy as np
import utils.geometry as geometry
import enum


class MeshingMethod(enum.Enum):
    POISSON = 1
    BALL_PIVOT = 2
    ALPHA = 3


def mesh_from_tree_pointcloud(
    tree_pointcloud: geometry.Pointcloud,
    meshing_method: MeshingMethod,
):
    """
    Mesh the point cloud of a tree object using Poisson reconstruction.

    :param tree: tree_pointcloud
        The tree point cloud to mesh.

    :param meshing_method: MeshingMethod
        The meshing method to use.


    """
    pcd = o3d.geometry.PointCloud()
    if meshing_method == MeshingMethod.POISSON:
        pcd.points = o3d.utility.Vector3dVector(tree_pointcloud.points)
        o3d_mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
            pcd, depth=9, width=0, scale=1.1, linear_fit=False
        )
    elif meshing_method == MeshingMethod.BALL_PIVOT:
        pcd.points = o3d.utility.Vector3dVector(tree_pointcloud.points)
        o3d_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
            pcd, o3d.utility.DoubleVector([0.01, 0.1])
        )
    elif meshing_method == MeshingMethod.ALPHA:
        pcd.points = o3d.utility.Vector3dVector(tree_pointcloud.points)
        o3d_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(
            pcd, alpha=2
        )
        mesh = geometry.Mesh(
            np.asarray(o3d_mesh.vertices),
            np.asarray(o3d_mesh.triangles),
            np.asarray(o3d_mesh.vertex_colors),
        )
        return mesh


def mesh_from_rhino_pointcloud(
    rhino_pointcloud: geometry.PointCloud,
    meshing_method: MeshingMethod,
    alpha: float = 2,
):
    """
    Mesh a geometry.PointCloud object using 3 different meshing methods.
    Note that by experience, the alpha method is the most reliable with my pointclouds.

    :param tree: rhino_pointcloud
        The Rhino point cloud to mesh.

    :param meshing_method: MeshingMethod
        The meshing method to use.

    """
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(
        [[point.X, point.Y, point.Z] for point in rhino_pointcloud]
    )
    if meshing_method == MeshingMethod.POISSON:
        pcd.estimate_normals()
        o3d_mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
            pcd, depth=3, width=0, scale=1.1, linear_fit=False
        )
    elif meshing_method == MeshingMethod.BALL_PIVOT:
        pcd.estimate_normals()
        o3d_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
            pcd, o3d.utility.DoubleVector([0.09, 0.25])
        )
    elif meshing_method == MeshingMethod.ALPHA:
        o3d_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(
            pcd, alpha=2
        )

    mesh = geometry.Mesh(
        np.asarray(o3d_mesh.vertices),
        np.asarray(o3d_mesh.triangles),
        np.asarray(o3d_mesh.vertex_colors),
    )
    return mesh
