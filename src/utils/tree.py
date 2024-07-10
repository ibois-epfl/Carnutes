import persistent
"""
Tree class to store tree data.
The point cloud of the tree is stored as a list of points
:param tree_id: The id of the tree
:param tree_name: The name of the tree
:param tree_point_cloud: The point cloud of the tree as a list of lists of 3 coordinates
"""
class Tree(persistent.Persistent):
    def __init__(self, tree_id, tree_name, tree_point_cloud):
        self.tree_id = tree_id
        self.tree_name = tree_name
        self.tree_point_cloud = tree_point_cloud

    def __str__(self):
        return f"Tree {self.tree_id} - {self.tree_name}"