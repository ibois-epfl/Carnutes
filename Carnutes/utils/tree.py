import persistent

class Tree(persistent.Persistent):
    def __init__(self, tree_id, tree_name, tree_point_cloud):
        self.tree_id = tree_id
        self.tree_name = tree_name
        self.tree_point_cloud = tree_point_cloud

    def __str__(self):
        return f"Tree {self.tree_id} - {self.tree_name}"