#! python3
# r: numpy==1.26.4
# r: open3d==0.18.0
# r: ZODB==6.0
# r: igraph==0.11.6

import os
import copy
import System

from utils import model, tree, geometry, interact_with_rhino
from utils import element as elem
from utils.tree import Tree
from packing import packing_manipulations

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
    # Ask user which element (s)he wants to replace with a point cloud
    (
        element_geometry,
        element_guid,
    ) = interact_with_rhino.select_single_element_to_replace()

    for element in current_model.elements:
        if element.GUID == element_guid:
            target = element
            break

    reference_pc_as_list = []
    # if isinstance(target.geometry, Rhino.Geometry.NurbsCurve):
    for vertex in current_model.connectivity_graph.graph.vs:
        if vertex["guid"] == target.GUID:
            incident_edges = vertex.all_edges()
            for edge in incident_edges:
                if edge.source == vertex:
                    target_edge = edge.target
                else:
                    target_edge = edge.source
                for element in current_model.elements:
                    if element.GUID == target_edge["guid"]:
                        reference_pc_as_list.append(element.geometry)
    # else:
    #     reference_pc_as_list.append(target.geometry)
    reference_pc = geometry.Pointcloud.from_geometry_list(reference_pc_as_list)
    reference_pc = packing_manipulations.crop_pointcloud(
        reference_pc, target.geometry.GetBoundingBox(False)
    )

    # Retrieve 1 random point cloud from the database
    current_dir = os.path.dirname(os.path.realpath(__file__))
    database_path = os.path.join(current_dir, "database", "point_cloud_database.fs")
    reader = db_reader.DatabaseReader(database_path)
    n_pc = reader.get_num_pointclouds()
    random_pc = reader.get_pointcloud(np.random.randint(0, n_pc))
    reader.close()

    # Align it using o3d's ransac, then crop it to the bounding box of the element
    adapted_pc = packing_manipulations.match_pointclouds(random_pc, reference_pc)
    adapted_pc = packing_manipulations.crop_pointcloud(
        adapted_pc, target.geometry.GetBoundingBox(False)
    )

    # Replace the element with the adapted point cloud
    current_model.replace_element(target, elem.Element(adapted_pc, target.GUID))
