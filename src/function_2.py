"""
This is a dummy function, to test out the bones of the project.
"""
#! python3
# r: pc_skeletor
# r: igraph

import os
import copy

import utils.database_reader as db_reader
from utils.tree import Tree

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
        tree_list = []
        skeleton_list = []
        skeleton_polyline_list = []
        for point in tree.tree_point_cloud:
            tree_list.append(list(point))
        for point in tree_list:
            rh_pointcloud.Add(Rhino.Geometry.Point3d(point[0],point[1], point[2]))
        for point in tree.tree_skeleton:
            skeleton_list.append(list(point))
        for point in skeleton_list:
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