"""
This is a dummy function, to test out the bones of the project.
"""
#! python3
# r: igraph
# r: ZODB

import os
import copy

import utils.database_reader as db_reader
from utils.tree import Tree

import System.Drawing
import Rhino
import scriptcontext as sc

def main():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    database_path = os.path.join(current_dir, 'database', 'tree_database.fs')
    reader = db_reader.DatabaseReader(database_path)

    n_tree = reader.get_num_trees()
    for i in range(n_tree):
        tree = reader.get_tree(i)
        tree = copy.deepcopy(tree)
        rh_pointcloud = Rhino.Geometry.PointCloud()
        rh_skeleton = Rhino.Geometry.PointCloud()
        skeleton_polyline_list = []

        for j in range(len(tree.point_cloud.points)):
            rh_pointcloud.Add(Rhino.Geometry.Point3d(tree.point_cloud.points[j][0],
                                                     tree.point_cloud.points[j][1],
                                                     tree.point_cloud.points[j][2]),
                              System.Drawing.Color.FromArgb(255,
                                                            int(tree.point_cloud.colors[j][0]*255),
                                                            int(tree.point_cloud.colors[j][1]*255),
                                                            int(tree.point_cloud.colors[j][2]*255)))
        for point in tree.skeleton.points:
            rh_skeleton.Add(Rhino.Geometry.Point3d(point[0],point[1], point[2]))
            skeleton_polyline_list.append(Rhino.Geometry.Point3d(point[0],point[1], point[2]))

        skeleton_polyline_list.sort(key=lambda x: x[2])
        polyline = Rhino.Geometry.Polyline(skeleton_polyline_list)
        sc.doc.Objects.AddPolyline(polyline)
        sc.doc.Objects.AddPointCloud(rh_pointcloud)
        sc.doc.Objects.AddPointCloud(rh_skeleton)
        print(tree)

    reader.close()

if __name__ == '__main__':
    main()
    print("Done")