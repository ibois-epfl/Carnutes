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

from utils import model, tree, geometry
from utils import element as elem
from utils.tree import Tree
from packing import packing_manipulations, packing_combinatorics

import numpy as np
import Rhino
import scriptcontext

def crop(tree : tree, bounding_volume : Rhino.Geometry.Brep):
    """
    Crop the tree to a bounding volume
    Used to be a method of the tree class but has been moved out to make the Tree class available for testing outside of rhino.
    
        
    :param bounding_volume: closed Brep
        The bounding Brep to crop the tree to
    """
    indexes_to_remove = []
    for i in range(len(tree.point_cloud.points)):
        point = tree.point_cloud.points[i]
        if not bounding_volume.IsPointInside(Rhino.Geometry.Point3d(point[0], point[1], point[2]), 0.01, True):
            indexes_to_remove.append(i)
    tree.point_cloud.points = [point for i, point in enumerate(tree.point_cloud.points) if i not in indexes_to_remove]
    tree.point_cloud.colors = [color for i, color in enumerate(tree.point_cloud.colors) if i not in indexes_to_remove]

def main():
    """
    1) create the model
    3) ask user which element (s)he wants to replace with a point cloud
    2) retrieve 1 random point cloud from the database
    4) align it using o3d's ransac, then crop it to the bounding box of the element
    """

    # Create the model
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt("Select the whole structure")
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Brep | Rhino.DocObjects.ObjectType.Curve
    go.GetMultiple(1, 1000)

    if go.CommandResult() != Rhino.Commands.Result.Success:
        print("No object selected.")
        return
    
    geometries = [go.Object(i).Geometry() for i in range(go.ObjectCount)]

    if len(geometries) < 2:
        print("At least two geometries are needed to create a graph.")
        return
    if isinstance(geometries[0], Rhino.Geometry.LineCurve):
        geometries = [geo.ToNurbsCurve() for geo in geometries]
        print("LineCurves converted to NurbsCurves")
    elif isinstance(geometries[0], Rhino.Geometry.Line):
        geometries = [geo.ToNurbsCurve() for geo in geometries]
        print("Lines converted to NurbsCurves")
    elif isinstance(geometries[0], Rhino.Geometry.Curve):
        geometries = [geo.ToNurbsCurve() for geo in geometries]
        print("Curves converted to NurbsCurve")

    elements = [elem.Element(geometries[i], go.Object(i).ObjectId) for i in range(go.ObjectCount)]
    current_model = model.Model(elements)

    # Ask user which element (s)he wants to replace with a point cloud
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt("Select the element to replace with a point cloud")
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Brep | Rhino.DocObjects.ObjectType.Curve
    go.GetMultiple(1, 1)
    if go.CommandResult() != Rhino.Commands.Result.Success:
        print("No object selected.")
        return
    element = go.Object(0).Geometry()
    element_guid = go.Object(0).ObjectId

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
                reference_pc_as_list.append(edge["location"])
            break
    # at this point the reference_pc_as_list should contain the points, but they are not ordered. We need to order them.
    # for this we assume that an element in the model has a principal direction, and we sort the points along this direction
    x_max_bounds = max([point[0] for point in reference_pc_as_list])
    x_min_bounds = min([point[0] for point in reference_pc_as_list])
    delta_x = x_max_bounds - x_min_bounds
    y_max_bounds = max([point[1] for point in reference_pc_as_list])
    y_min_bounds = min([point[1] for point in reference_pc_as_list])
    delta_y = y_max_bounds - y_min_bounds
    z_max_bounds = max([point[2] for point in reference_pc_as_list])
    z_min_bounds = min([point[2] for point in reference_pc_as_list])
    delta_z = z_max_bounds - z_min_bounds
    if delta_x > delta_y and delta_x > delta_z:
        reference_pc_as_list = sorted(reference_pc_as_list, key=lambda x: x[0])
    elif delta_y > delta_x and delta_y > delta_z:
        reference_pc_as_list = sorted(reference_pc_as_list, key=lambda x: x[1])
    elif delta_z > delta_x and delta_z > delta_y:
        reference_pc_as_list = sorted(reference_pc_as_list, key=lambda x: x[2])
    # Retrieve the best fitting tree from the database
    reference_skeleton = geometry.Pointcloud(reference_pc_as_list)
    current_dir = os.path.dirname(os.path.realpath(__file__))
    database_path = os.path.join(current_dir, 'database', 'tree_database.fs')
    my_tree,  best_reference, best_target, best_db_level_rmse = packing_combinatorics.find_best_tree(reference_skeleton, 100.0, database_path, return_rmse=True)

    # Align it using o3d's ransac, then crop it to the bounding box of the element
    my_tree.align_to_skeleton(reference_skeleton)

    # Brep to crop the point cloud
    if isinstance(target.geometry, Rhino.Geometry.NurbsCurve):
        cylinder = Rhino.Geometry.Brep.CreatePipe(target.geometry, 1, True, Rhino.Geometry.PipeCapMode.Flat, True, 0.01, 0.01)[0]
    elif isinstance(target.geometry, Rhino.Geometry.Brep):
        edges = [target.geometry.Edges[i] for i in range(target.geometry.Edges.Count) if not target.geometry.Edges[i].IsClosed]
        cylinder = Rhino.Geometry.Brep.CreatePipe(edges[0], 1, True, Rhino.Geometry.PipeCapMode.Flat, True, 0.01, 0.01)[0]
        # cylinder = Rhino.Geometry.Brep.CreatePipe(reference_crv_for_brep, 1, True, Rhino.Geometry.PipeCapMode.Flat, True, 0.01, 0.01)[0]
    else:
        raise ValueError("The geometry of the target element is not supported.")
    crop(my_tree, cylinder)
    my_tree.create_mesh()

    tree_mesh = Rhino.Geometry.Mesh()
    for i in range(len(my_tree.mesh.vertices)):
        tree_mesh.Vertices.Add(my_tree.mesh.vertices[i][0], my_tree.mesh.vertices[i][1], my_tree.mesh.vertices[i][2])
    for i in range(len(my_tree.mesh.faces)):
        tree_mesh.Faces.AddFace(int(my_tree.mesh.faces[i][0]), int(my_tree.mesh.faces[i][1]),int(my_tree.mesh.faces[i][2]))
    for i in range(len(my_tree.mesh.colors)):
        tree_mesh.VertexColors.Add(System.Drawing.Color.FromArgb(int(my_tree.mesh.colors[i][0]*255),
                                                                  int(my_tree.mesh.colors[i][1]*255),
                                                                  int(my_tree.mesh.colors[i][2]*255)))
    scriptcontext.doc.Objects.AddMesh(tree_mesh)

    # Create the point cloud
    my_tree_pc_rh = Rhino.Geometry.PointCloud()
    for j in range(len(my_tree.point_cloud.points)):
            my_tree_pc_rh.Add(Rhino.Geometry.Point3d(my_tree.point_cloud.points[j][0],
                                                     my_tree.point_cloud.points[j][1],
                                                     my_tree.point_cloud.points[j][2]),
                              System.Drawing.Color.FromArgb(255,
                                                            int(my_tree.point_cloud.colors[j][0] * 255),
                                                            int(my_tree.point_cloud.colors[j][1] * 255),
                                                            int(my_tree.point_cloud.colors[j][2] * 255)))
    scriptcontext.doc.Objects.AddPointCloud(my_tree_pc_rh)

    my_tree_skeleton_rh = Rhino.Geometry.PointCloud()
    for point in my_tree.skeleton.points:
        my_tree_skeleton_rh.Add(Rhino.Geometry.Point3d(point[0],point[1], point[2]))
    scriptcontext.doc.Objects.AddPointCloud(my_tree_skeleton_rh)

if __name__ == "__main__":
    main()
    print("Done")