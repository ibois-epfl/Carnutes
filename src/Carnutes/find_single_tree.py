"""
This is a dummy function, to test out the bones of the project.
"""

#! python3
# r: numpy==1.26.4
# r: open3d==0.18.0
# r: ZODB==6.0
# r: igraph==0.11.6

import os
import copy
import System

from utils import model, tree, geometry, interact_with_rhino, conversions
from utils import element as elem
from utils.tree import Tree
from packing import packing_combinatorics

import numpy as np
import Rhino
import scriptcontext


def crop(tree: tree, bounding_volume: Rhino.Geometry.Brep):
    """
    Crop the tree to a bounding volume
    Used to be a method of the tree class but has been moved out to make the Tree class available for testing outside of rhino.


    :param bounding_volume: closed Brep
        The bounding Brep to crop the tree to
    """
    indexes_to_remove = []
    for i in range(len(tree.point_cloud.points)):
        point = tree.point_cloud.points[i]
        if not bounding_volume.IsPointInside(
            Rhino.Geometry.Point3d(point[0], point[1], point[2]), 0.01, True
        ):
            indexes_to_remove.append(i)
    tree.point_cloud.points = [
        point
        for i, point in enumerate(tree.point_cloud.points)
        if i not in indexes_to_remove
    ]
    tree.point_cloud.colors = [
        color
        for i, color in enumerate(tree.point_cloud.colors)
        if i not in indexes_to_remove
    ]


def main():
    """
    1) create the model
    3) ask user which element (s)he wants to replace with a point cloud
    2) retrieve 1 random point cloud from the database
    4) align it using o3d's ransac, then crop it to the bounding box of the element
    """

    # Create the model
    current_model = interact_with_rhino.create_model_from_rhino_selection()
    if current_model is None:
        return

    # Ask user which element (s)he wants to replace with a point cloud
    (
        element_geometry,
        element_guid,
    ) = interact_with_rhino.select_single_element_to_replace()

    for element in current_model.elements:
        if element.GUID == element_guid:
            target = element
            reference_diameter = element.diameter
            break

    reference_pc_as_list = []
    # if isinstance(target.geometry, Rhino.Geometry.NurbsCurve):
    for vertex in current_model.connectivity_graph.graph.vs:
        if vertex["guid"] == target.GUID:
            incident_edges = vertex.all_edges()
            for edge in incident_edges:
                reference_pc_as_list.append(edge["location"])
            break

    # removing duplicates
    for i in range(len(reference_pc_as_list)):
        for j in range(i + 1, len(reference_pc_as_list)):
            if np.allclose(reference_pc_as_list[i], reference_pc_as_list[j]):
                reference_pc_as_list.pop(j)
                break

    # at this point the reference_pc_as_list should contain the points, but they are not ordered. We need to order them.
    reference_pc_as_list = geometry.sort_points(reference_pc_as_list)

    # Retrieve the best fitting tree from the database
    reference_skeleton = geometry.Pointcloud(reference_pc_as_list)
    current_dir = os.path.dirname(os.path.realpath(__file__))
    database_path = os.path.join(current_dir, "database", "tree_database.fs")
    (my_tree, best_target, best_db_level_rmse, best_init_rotation) = (
        packing_combinatorics.find_best_tree_unoptimized(
            reference_skeleton, reference_diameter, database_path, return_rmse=True
        )
    )

    if my_tree is None:
        raise ValueError("No best tree found, mission aborted")

    print("mean diameter of selected_tree = ", my_tree.mean_diameter)
    # Align it using o3d's ransac, then crop it to the bounding box of the element
    my_tree.align_to_skeleton(reference_skeleton)

    # Brep to crop the point cloud
    cylinder = target.create_bounding_cylinder(radius=1)
    crop(my_tree, cylinder)
    my_tree.create_mesh()

    tree_mesh = conversions.convert_carnutes_mesh_to_rhino_mesh(my_tree.mesh)
    scriptcontext.doc.Objects.AddMesh(tree_mesh)


if __name__ == "__main__":
    main()
    print("Done")
