import os

dir_path = os.path.dirname(os.path.abspath(__file__))
REGISTER_SCHEMA_PATH = '{}/{}'.format(dir_path, 'schemas/register.json')
FORGET_PASS_SCHEMA_PATH = '{}/{}'.format(dir_path, 'schemas/forget_pass.json')
ACTIVATE_ACCOUNT_SCHEMA_PATH = '{}/{}'.format(dir_path,
                                              'schemas/activate_account.json')
