#! python3
import ZODB
import open3d as o3d
import ZODB.FileStorage

import os
import sys
import transaction
import BTrees.OOBTree

import utils.tree as tree

def create_database():
    storage = ZODB.FileStorage.FileStorage('Carnutes/database/tree_database.fs')
    db = ZODB.DB(storage)
    connection = db.open()
    root = connection.root

    tree_pc = o3d.io.read_point_cloud("dataset/test_file.ply")
    tree_pc = tree_pc.voxel_down_sample(voxel_size=2)
    tree_list = []
    for point in tree_pc.points:
        tree_list.append([point[0], point[1], point[2]])
    tree1 = tree.Tree(1, "Tree 1", tree_list)


    root.trees = BTrees.OOBTree.BTree()
    root.trees[tree1.tree_id] = tree1

    transaction.commit()
    connection.close()

if __name__ == '__main__':
    create_database()