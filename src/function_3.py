"""
This is a dummy function, to test out the bones of the project.
"""
#! python3

import os
import sys
import copy
import System
import platform

# Thanks to https://discourse.mcneel.com/t/rhinocode-scripeditor-for-development-of-libraries/175228/22

CONDA_ENV = r'/Users/admin/anaconda3/envs/database_creation'

if platform.system() == 'Windows':
    sys.path.append(os.path.join(CONDA_ENV, r'Lib\site-packages'))
    os.add_dll_directory(os.path.join(CONDA_ENV, r'Library/bin'))

elif platform.system() == 'Darwin':  # Darwin stands for macOS
    sys.path.append(os.path.join(CONDA_ENV, r'lib/python3.9/site-packages'))
    os.environ["DYLD_LIBRARY_PATH"] = os.path.join(CONDA_ENV, r'bin')

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
    
    print("Element selected: {}".format(element_guid))

    
    # Retrieve 1 random point cloud from the database
    current_dir = os.path.dirname(os.path.realpath(__file__))
    database_path = os.path.join(current_dir, 'database', 'tree_database.fs')
    reader = database_reader.DatabaseReader(database_path)
    n_tree = reader.get_num_trees()
    tree_id = np.random.randint(0, n_tree)
    my_tree = reader.get_tree(tree_id)
    my_tree = copy.deepcopy(my_tree)
    

    # Align it using o3d's ransac, then crop it to the bounding box of the element
    target_skeleton = geometry.Pointcloud(reference_pc_as_list)
    my_tree.align_to_skeleton(target_skeleton)

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
    reader.close()
    scriptcontext.doc.Objects.AddPointCloud(my_tree_pc_rh)
    print("Point cloud added to the model.")
if __name__ == "__main__":
    main()
    print("Done")

