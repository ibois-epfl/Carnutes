"""
Main module for reading the database, containing the DatabaseReader class.
"""
#! python3

import atexit

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
        self.is_open = True
        

    def get_tree(self, tree_id):
        """
        Get a tree from the database, using its id.
        """
        try:
            return self.root.trees[tree_id]
        except KeyError:
            print(f"Tree with id {tree_id} not found in the database. \n I was removed in a previous query.")
            return None
    
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
        self.is_open = False
    
    # def __del__(self):
    #     """
    #     Note: This method is not guaranteed to be called, as it depends on the garbage collector.
    #     """
    #     if self.is_open:
    #         self.close()
    #     print("DatabaseReader object deleted automatically. \n Ideally it should be done manually asap in the code.")