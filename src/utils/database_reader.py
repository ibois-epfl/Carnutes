#! python3
import ZODB
import ZODB.FileStorage

class DatabaseReader:
    def __init__(self, database_path):
        self.storage = ZODB.FileStorage.FileStorage(database_path)
        self.db = ZODB.DB(self.storage)
        self.connection = None
        self.root = None
        

    def get_tree(self, tree_id):
        return self.root.trees[tree_id]

    def close(self):
        self.connection.close()
        self.db.close()
        self.storage.close()