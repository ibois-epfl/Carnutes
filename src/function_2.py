#! python3
# r: ZODB
# r: numpy

import os
import copy
import numpy as np

import utils.database_reader as db_reader
import Rhino
import scriptcontext as sc
def get_tree(tree_id):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    database_path = os.path.join(current_dir, 'database', 'tree_database.fs')
    reader = db_reader.DatabaseReader(database_path)
    reader.connection = reader.db.open()
    reader.root = reader.connection.root
    tree = reader.get_tree(tree_id)
    tree = copy.deepcopy(tree)
    reader.close()
    return tree

if __name__ == '__main__':
    tree = get_tree(1)
    rh_pointcloud = Rhino.Geometry.PointCloud()
    tree_list = []
    for point in tree.tree_point_cloud:
        tree_list.append(list(point))
    for point in tree_list:
        rh_pointcloud.Add(Rhino.Geometry.Point3d(point[0],point[1], point[2]))
    sc.doc.Objects.AddPointCloud(rh_pointcloud)
    print(tree)