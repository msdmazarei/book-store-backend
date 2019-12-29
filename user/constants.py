import configs
import os

dir_path = os.path.dirname(os.path.abspath(__file__))

USER_ADD_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/user_add.json')
USER_EDIT_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/user_edit.json')
PERSON_ADD_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/person_add.json')
PERSON_EDIT_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/person_edit.json')

RESET_PASS_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/reset_pass.json')


ADMINISTRATORS_USERNAMES = configs.ADMINISTRATORS