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

# import Rhino

import os
import transaction
import BTrees.OOBTree
import time

import utils.tree as tree
import utils.database_reader as database_reader


def main(voxel_size=0.03, working_dir=os.path.dirname(os.path.realpath(__file__))):
    database_folder = os.path.join(working_dir, "database")
    if not os.path.exists(database_folder):
        os.makedirs(database_folder)

    db_reader = database_reader.DatabaseReader(
        os.path.join(working_dir, "database/tree_database.fs")
    )

    for i, pc_file in enumerate(os.listdir(os.path.join(working_dir, "dataset"))):

        if pc_file.endswith(".ply"):
            print(f"Processing {pc_file}")
            pc = o3d.io.read_point_cloud(
                os.path.join(working_dir, f"dataset/{pc_file}")
            )
            pc = pc.voxel_down_sample(voxel_size)
            pc, indexes = pc.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)

            tree_pc_as_pt_list = []
            tree_colors_as_list = []

            for j in range(len(pc.points)):
                tree_pc_as_pt_list.append(
                    [
                        float(pc.points[j][0]),
                        float(pc.points[j][1]),
                        float(pc.points[j][2]),
                    ]
                )
                tree_colors_as_list.append(
                    [
                        float(pc.colors[j][0]),
                        float(pc.colors[j][1]),
                        float(pc.colors[j][2]),
                    ]
                )

            tree_for_db = tree.Tree(
                i,
                f"tree_{i}",
                tree.Pointcloud(tree_pc_as_pt_list, tree_colors_as_list),
            )
            tree_for_db.compute_skeleton()

            db_reader.root.trees[tree_for_db.id] = tree_for_db

    db_reader.root.n_trees = len(db_reader.root.trees)

    transaction.commit()
    db_reader.pack()  # We dont' want to keep previous revisions. We only want the latest one.
    db_reader.close()
    db_reader.delete_old()  # We don't want to keep the fs.old file either.


if __name__ == "__main__":

    # WORKING_DIR = os.path.dirname(os.path.realpath(__file__))

    # # Get from user the voxel size
    # gn = Rhino.Input.Custom.GetNumber()
    # gn.SetCommandPrompt("Enter the voxel size")
    # gn.SetDefaultNumber(0.03)
    # gn.Get()

    # VOXEL_SIZE = gn.Number()
    starting_time = time.time()
    main()
    print(f"Execution time: {time.time() - starting_time}")
    print("Done")
