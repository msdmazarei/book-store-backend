import os

dir_path = os.path.dirname(os.path.abspath(__file__))
ADD_SCHEMA_PATH = '{}/{}'.format(dir_path, 'schemas/add.json')
RENAME_SCHEMA_PATH = '{}/{}'.format(dir_path, 'schemas/rename.json')
COLLECTION_SCHEMA_PATH = '{}/{}'.format(dir_path, 'schemas/collection.json')


BOOK_COLLECTION_SCHEMA_PATH = '{}/{}'.format(dir_path,
                                             'schemas/book_to_collection.json')
DELETE_BOOK_COLLECTION_SCHEMA_PATH = '{}/{}'.format(dir_path,
                                                    'schemas/delete_book_collection.json')
