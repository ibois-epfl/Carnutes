#! python3
# r: numpy==1.26.4
# r: open3d==0.18.0
# r: ZODB==6.0
# r: igraph==0.11.6

import os
import copy
import System
import time

from utils import tree, geometry, interact_with_rhino, conversions
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
    # ask the user for the optimisation basis:
    optimisation_basis = 3
    optimisation_basis = Rhino.Input.RhinoGet.GetInteger(
        "please provide the basis for the optimisation. The higher the number, the longer the calculation, but potentially the tree consumption will be lower\n default = 3",
        True,
        optimisation_basis,
        0,
        30,
    )

    # Create the model
    current_model = interact_with_rhino.create_model_from_rhino_selection()

    # For each element in the model, replace it with a point cloud. Starting from the elements with the highest degree.
    db_path = os.path.dirname(os.path.realpath(__file__)) + "/database/tree_database.fs"

    all_rmse = []

    for element in current_model.elements:
        if element.type == elem.ElementType.Point:
            continue
        reference_pc_as_list = []
        element_guid = element.GUID
        target_diameter = element.diameter
        reference_pc_as_list = element.locations

        # at this point the reference_pc_as_list should contain the points, but they are not ordered. We need to order them.
        reference_pc_as_list = geometry.sort_points(reference_pc_as_list)
        reference_skeleton = geometry.Pointcloud(reference_pc_as_list)
        (best_tree, best_target, best_rmse, best_init_rotation) = (
            packing_combinatorics.find_best_tree_optimized(
                reference_skeleton,
                target_diameter,
                db_path,
                optimisation_basis=3,
                return_rmse=True,
            )
        )
        if best_tree is None:
            print("No tree found. Skiping this element.")
            continue

        all_rmse.append(best_rmse)
        best_tree = copy.deepcopy(best_tree)

        best_tree.align_to_skeleton(reference_skeleton)

        # Create a bounding volume for the element
        bounding_volume = element.create_bounding_cylinder(radius=1)
        crop(best_tree, bounding_volume)
        best_tree.create_mesh()

        tree_mesh = conversions.convert_carnutes_mesh_to_rhino_mesh(best_tree.mesh)
        scriptcontext.doc.Objects.AddMesh(tree_mesh)

    return all_rmse


if __name__ == "__main__":
    init_time = time.time()
    all_rmse = main()
    end_time = time.time()
    print(f"Execution time: {end_time - init_time}")
    print(f"The mean rmse fitting {len(all_rmse)} elements is {np.mean(all_rmse)}")
    print("Done")
