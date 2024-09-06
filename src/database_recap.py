"""
This function displays a pop-up window with a summary of the database's contents.
"""
#! python3
# r: numpy==1.26.4
# r: open3d==0.18.0
# r: ZODB==6.0
# r: igraph==0.11.6

import ZODB
import ZODB.FileStorage
import Rhino

import os

import utils.tree as tree
import utils.database_reader as database_reader

def recap_database():
    """
    Display a pop-up window with a summary of the database's contents.
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    database_path = os.path.join(current_dir, "database", "tree_database.fs")
    reader = database_reader.DatabaseReader(database_path)
    n_trees = reader.get_num_trees()
    message = []
    diameters = []
    heights = []
    # get individual info about each tree
    for i in range(n_trees):
        current_tree = reader.get_tree(i)
        diameters.append(current_tree.mean_diameter)
        heights.append(current_tree.height)

    diameters, heights = zip(*sorted(zip(diameters, heights)))
    
    # calculate the deciles based on diameters
    deciles = []
    for i in range(1, 11):
        deciles.append(diameters[int(i * n_trees / 11)])
    deciles.append(diameters[-1])

    corresponding_summed_heights = []
    for i in range(11):
        corresponding_summed_heights.append(sum([height for j, height in enumerate(heights) if diameters[j] <= deciles[i] and diameters[j] > deciles[i - 1]]))

    reader.close()

    for i in range(1,11):
        message.append(
            f"{i}th decile: diameters between {deciles[i - 1]:.2f}m and {deciles[i]:.2f}m have a total height of {corresponding_summed_heights[i]:.2f} meters."
        )

    Rhino.UI.Dialogs.ShowMultiListBox(
        "Database Summary",
        f"The database contains {n_trees} trees: \n",
       message
    )

if __name__ == "__main__":
    recap_database()