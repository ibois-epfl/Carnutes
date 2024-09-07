#! python3
# r: numpy==1.26.4
# r: open3d==0.18.0
# r: ZODB==6.0
# r: igraph==0.11.6

import os
import copy
import System

from utils import model, tree, geometry, interact_with_rhino, database_reader
from utils import element as elem
from utils.tree import Tree
from packing import packing_manipulations, packing_combinatorics

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
    # Create the model
    current_model = interact_with_rhino.create_model_from_rhino_selection()

    # For each element in the model, replace it with a point cloud. Starting from the elements with the highest degree.
    elements = current_model.elements
    elements.sort(key=lambda x: x.degree, reverse=True)
    for element in elements:
        print(f"Element {element.GUID} has degree {element.degree}")

    db_path = os.path.dirname(os.path.realpath(__file__)) + "/database/tree_database.fs"

    for element in elements:
        reference_pc_as_list = []
        element_guid = element.GUID
        target_diameter = element.diameter
        reference_pc_as_list = element.locations

        # at this point the reference_pc_as_list should contain the points, but they are not ordered. We need to order them.
        reference_pc_as_list = geometry.sort_points(reference_pc_as_list)
        reference_skeleton = geometry.Pointcloud(reference_pc_as_list)
        (
            best_tree,
            best_reference,
            best_target,
            best_rmse,
        ) = packing_combinatorics.find_best_tree(
            reference_skeleton, target_diameter, db_path, return_rmse=True
        )
        if best_tree is None:
            raise ValueError("No best tree found, mission aborted")
        best_tree = copy.deepcopy(best_tree)

        best_tree.align_to_skeleton(reference_skeleton)

        # Create a bounding volume for the element
        bounding_volume = element.create_bounding_cylinder(radius=1)
        crop(best_tree, bounding_volume)
        best_tree.create_mesh()

        tree_mesh = Rhino.Geometry.Mesh()
        for i in range(len(best_tree.mesh.vertices)):
            tree_mesh.Vertices.Add(
                best_tree.mesh.vertices[i][0],
                best_tree.mesh.vertices[i][1],
                best_tree.mesh.vertices[i][2],
            )
        for i in range(len(best_tree.mesh.faces)):
            tree_mesh.Faces.AddFace(
                int(best_tree.mesh.faces[i][0]),
                int(best_tree.mesh.faces[i][1]),
                int(best_tree.mesh.faces[i][2]),
            )
        for i in range(len(best_tree.mesh.colors)):
            tree_mesh.VertexColors.Add(
                System.Drawing.Color.FromArgb(
                    int(best_tree.mesh.colors[i][0] * 255),
                    int(best_tree.mesh.colors[i][1] * 255),
                    int(best_tree.mesh.colors[i][2] * 255),
                )
            )
        scriptcontext.doc.Objects.AddMesh(tree_mesh)


if __name__ == "__main__":
    main()
    print("Done")
