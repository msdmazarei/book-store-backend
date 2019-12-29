import os

dir_path = os.path.dirname(os.path.abspath(__file__))
DEVICE_KEY_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/device_key.json')
PREPARE_BOOK_SCHEMA_PATH = '{}/{}'.format(dir_path,'schemas/prepare_book.json')