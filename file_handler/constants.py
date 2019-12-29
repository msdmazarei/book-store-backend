import os

dir_path = os.path.dirname(os.path.abspath(__file__))
UPLOAD_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/upload_file.json')
DELETE_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/delete_files.json')