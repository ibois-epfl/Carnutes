"""
This function resets the database by overwriting the existing database with a new one, using the trees from the dataset folder.
"""

#! python3
# r: numpy==1.26.4
# r: open3d==0.18.0
# r: ZODB==6.0
# r: igraph==0.11.6

import ZODB
import ZODB.FileStorage
import open3d as o3d
import Rhino

import os
import transaction
import BTrees.OOBTree

import utils.tree as tree

def main():
    database_folder = os.path.join(WORKING_DIR, 'database')
    if not os.path.exists(database_folder):
        os.makedirs(database_folder)

    storage = ZODB.FileStorage.FileStorage(os.path.join(WORKING_DIR, 'database/tree_database.fs'))
    db = ZODB.DB(storage)
    connection = db.open()
    root = connection.root
    root.trees = BTrees.OOBTree.BTree()
    i = 0

    for pc_file in os.listdir(os.path.join(WORKING_DIR, "dataset")):
            
            if pc_file.endswith(".ply"):
                print(f"Processing {pc_file}")
                pc = o3d.io.read_point_cloud(os.path.join(WORKING_DIR,f"dataset/{pc_file}"))
                pc = pc.voxel_down_sample(VOXEL_SIZE)
    
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
    db.close()
    storage.close()
    
if __name__ == '__main__':
    
    WORKING_DIR = os.path.dirname(os.path.realpath(__file__))

    # Get from user the voxel size
    gn = Rhino.Input.Custom.GetNumber()
    gn.SetCommandPrompt("Enter the voxel size")
    gn.SetDefaultNumber(0.05)
    gn.Get()

    VOXEL_SIZE = gn.Number()

    main()

    print("Done")
