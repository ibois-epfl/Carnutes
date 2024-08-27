#! python3

import ZODB
import open3d as o3d
import ZODB.FileStorage

import os
import sys
import transaction
import BTrees.OOBTree

import utils.tree as tree

def create_database(voxel_size=0.05):
    """
    Create a database of trees from the point cloud dataset.

    :param voxel_size: float, optional
        The size of the voxel grid used for downsampling the point cloud. The default is 0.05.
    """
    database_folder = 'database'
    if not os.path.exists(database_folder):
        os.makedirs(database_folder)

    storage = ZODB.FileStorage.FileStorage('database/tree_database.fs')
    db = ZODB.DB(storage)
    connection = db.open()
    root = connection.root
    root.trees = BTrees.OOBTree.BTree()
    i = 0
    for pc_file in os.listdir("dataset"):
        
        if pc_file.endswith(".ply"):
            print(f"Processing {pc_file}")
            pc = o3d.io.read_point_cloud(f"dataset/{pc_file}")
            pc = pc.voxel_down_sample(voxel_size)

            tree_pc_as_pt_list = []
            tree_colors_as_list = []
            
            for j in range(len(pc.points)):
                tree_pc_as_pt_list.append([float(pc.points[j][0]), 
                                           float(pc.points[j][1]), 
                                           float(pc.points[j][2])])
                tree_colors_as_list.append([float(pc.colors[j][0]),
                                            float(pc.colors[j][1]),
                                            float(pc.colors[j][2])])
                
                
            tree_for_db = tree.Tree(len(root.trees), f"tree_{i}", tree.Pointcloud(tree_pc_as_pt_list, tree_colors_as_list))
            tree_for_db.compute_skeleton()

            root.trees[tree_for_db.id] = tree_for_db
            i += 1

    root.n_trees = len(root.trees)

    transaction.commit()
    connection.close()

def augment_database():
    """
    Augment the database with new trees. To be implemented.
    """
    pass

if __name__ == '__main__':
    create_database(voxel_size=0.05)