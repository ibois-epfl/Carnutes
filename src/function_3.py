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

import numpy as np

import Rhino
import scriptcontext

from utils import database_reader, model, tree, geometry
from utils.tree import Tree

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

    elements = [model.Element(geometries[i], go.Object(i).ObjectId) for i in range(go.ObjectCount)]
    current_model = model.Model(elements)

    # small test to show all the connections of the element 10 of the model
    # connections = current_model.connectivity_graph.graph.incident(10)
    # for connection in connections:
    #     connection_location = current_model.connectivity_graph.graph.es[connection]['location']
    #     sphere = Rhino.Geometry.Sphere(Rhino.Geometry.Point3d(connection_location[0], connection_location[1], connection_location[2]), 1)
    #     scriptcontext.doc.Objects.AddSphere(sphere)
    
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
    if isinstance(target.geometry, Rhino.Geometry.NurbsCurve):
        crv_parameters = target.geometry.DivideByCount(30, True)
        for i in range(len(crv_parameters)):
            reference_pc_as_list.append([target.geometry.PointAt(crv_parameters[i]).X,
                                         target.geometry.PointAt(crv_parameters[i]).Y,
                                         target.geometry.PointAt(crv_parameters[i]).Z])
    elif isinstance(target.geometry, Rhino.Geometry.Brep):
        end_centers = []
        # We assume a pipe or cylinder: 3 faces of which two circular, and one rectangular wrapped around the two circular faces
        for edge in target.geometry.Edges:
            if not edge.IsClosed:
                reference_crv_for_brep = edge.ToNurbsCurve()
            elif edge.IsClosed:
                nurbs_version = edge.ToNurbsCurve()
                if nurbs_version.IsCircle():
                    circle = nurbs_version.TryGetCircle()[1]
                    center = circle.Center
                    end_centers.append(center)
        translation_vector =( (end_centers[1] - reference_crv_for_brep.PointAtEnd) + (end_centers[0] - reference_crv_for_brep.PointAtStart) )/ 2
        reference_crv_for_brep.Translate(translation_vector)
        crv_parameters = reference_crv_for_brep.DivideByCount(30, True)
        for i in range(len(crv_parameters)):
            reference_pc_as_list.append([reference_crv_for_brep.PointAt(crv_parameters[i]).X,
                                         reference_crv_for_brep.PointAt(crv_parameters[i]).Y,
                                         reference_crv_for_brep.PointAt(crv_parameters[i]).Z])


    
    # Retrieve 1 random point cloud from the database
    current_dir = os.path.dirname(os.path.realpath(__file__))
    database_path = os.path.join(current_dir, 'database', 'tree_database.fs')
    reader = database_reader.DatabaseReader(database_path)
    n_tree = reader.get_num_trees()
    tree_id = np.random.randint(0, n_tree)
    my_tree = reader.get_tree(tree_id)
    my_tree = copy.deepcopy(my_tree)
    reader.close()

    # Align it using o3d's ransac, then crop it to the bounding box of the element
    target_skeleton = geometry.Pointcloud(reference_pc_as_list)
    my_tree.align_to_skeleton(target_skeleton)

    # Brep to crop the point cloud
    cylinder = Rhino.Geometry.Brep.CreatePipe(target.geometry, 1, True, Rhino.Geometry.PipeCapMode.Flat, True, 0.01, 0.01)[0]
    my_tree.crop(cylinder)
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


    # crop the point cloud to a cylinder around the element
    if isinstance(target.geometry, Rhino.Geometry.NurbsCurve):
        cylinder = Rhino.Geometry.Brep.CreatePipe(target.geometry, 1, True, Rhino.Geometry.PipeCapMode.Flat, True, 0.01, 0.01)[0]
    else:
        cylinder = Rhino.Geometry.Brep.CreatePipe(reference_crv_for_brep, 1, True, Rhino.Geometry.PipeCapMode.Flat, True, 0.01, 0.01)[0]
    indexes_to_remove = []
    for i in range(my_tree_pc_rh.Count):
        point = my_tree_pc_rh[i]
        if not cylinder.IsPointInside(point.Location, 0.01, True):
            indexes_to_remove.append(i)
    
    my_tree_pc_rh.RemoveRange(indexes_to_remove)

    scriptcontext.doc.Objects.AddPointCloud(my_tree_pc_rh)

    print("Point cloud added to the model.")
if __name__ == "__main__":
    main()
    print("Done")