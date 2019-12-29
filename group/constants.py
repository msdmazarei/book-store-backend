import os

dir_path = os.path.dirname(os.path.abspath(__file__))

GROUP_ADD_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/group_add.json')
GROUP_EDIT_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/group_edit.json')

USER_ADD_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/user_add.json')
USER_GROUP_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/user_to_group.json')
