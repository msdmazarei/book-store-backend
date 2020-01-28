import os

dir_path = os.path.dirname(os.path.abspath(__file__))
KIPO_SCHEMA_PATH = '{}/{}'.format(dir_path, 'schemas/kipo_pay.json')
CHECKOUT_ADD_SCHEMA_PATH = '{}/{}'.format(dir_path,
                                          'schemas/checkout_press_payment_add.json')
CHECKOUT_EDIT_SCHEMA_PATH = '{}/{}'.format(dir_path,
                                           'schemas/checkout_press_payment_edit.json')
