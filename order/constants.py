import os

dir_path = os.path.dirname(os.path.abspath(__file__))
ORDER_ADD_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/order_add.json')
ORDER_EDIT_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/order_edit.json')

ITEM_ADD_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/item_add.json')
ITEM_EDIT_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/item_edit.json')

CHECKOUT_EDIT_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/checkout.json')
