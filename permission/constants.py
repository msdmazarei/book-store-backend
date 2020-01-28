import os

dir_path = os.path.dirname(os.path.abspath(__file__))
PERMISSION_ADD_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/permission_add.json')
PERMISSION_EDIT_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/permission_edit.json')

GROUP_ADD_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/group_add.json')
A_GROUP_ADD_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/a_group_add.json')