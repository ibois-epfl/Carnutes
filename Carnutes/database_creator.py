#! python3
import ZODB
import ZODB.FileStorage

import os
import sys
import transaction

def create_database():
    storage = ZODB.FileStorage.FileStorage('Carnutes/database/tree_database.fs')
    db = ZODB.DB(storage)
    connection = db.open()
    root = connection.root

    transaction.commit()
    connection.close()

if __name__ == '__main__':
    create_database()