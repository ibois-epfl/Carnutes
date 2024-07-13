"""
Main module for reading the database, containing the DatabaseReader class.
"""
#! python3
import ZODB
import ZODB.FileStorage

class DatabaseReader:
    """
    DatabaseReader class
    This class is used to read the database created by the database_creator.py script.
    
    :param database_path: str , The path to the database file (ends with .fs)
    
    Attributes:
        storage: ZODB.FileStorage.FileStorage
            The file storage object that is used to read the database file.
        db: ZODB.DB
            The database object that is used to access the database.
        connection: ZODB.connection
            The connection object that is used to connect to the database.
        root: ZODB.persistent.mapping.PersistentMapping
            The root object of the database.
    """
    def __init__(self, database_path):
        self.storage = ZODB.FileStorage.FileStorage(database_path)
        self.db = ZODB.DB(self.storage)
        self.connection = self.db.open()
        self.root = self.connection.root
        

    def get_tree(self, tree_id):
        """
        Get a tree from the database, using its id.
        """
        return self.root.trees[tree_id]
    
    def get_num_trees(self):
        """
        Get the number of trees in the database.
        This number is calculated at the creation of the database.
        """
        return self.root.n_trees

    def close(self):
        """
        Close the connection to the database.
        """
        self.connection.close()
        self.db.close()
        self.storage.close()