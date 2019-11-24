import json
import os

from celery import Celery

from configs import CELERY_DATABASE_URI
from helper import value
from messages import Message
from run_process.call_process import execute_process

temprory_saving_path = value('temprory_saving_path', '/tmp')
book_saving_path = value('book_saving_path', '/home/nsm/book_sources')

app = Celery('jjp', backend=CELERY_DATABASE_URI,
             broker='pyamqp://guest@localhost//')

app.config_from_object('celery_works.celeryconfig')

task_routes = {
    'sms': {'queue': 'sms'},
    'book_generate': {'queue': 'book_generate'}
}


@app.task(name='book_generate', bind=True)
def generate_book_content(self, data, **kwargs):
    # TODO run process
    json_file_name, out_file_name, final_file_name = save_json_file(data)
    print('json_file_name, out_file_name, final_file_name ', json_file_name,
          out_file_name, final_file_name)


    result = execute_process([json_file_name, out_file_name], username=None)

    os.remove(json_file_name)
    os.rename(out_file_name, final_file_name)
    print('result is : ', result)

    return data


@app.task(name='sms', bind=True)
def xsum(numbers):
    return sum(numbers)


def save_json_file(data):
    content_id = data.get('content_id')
    del data['content_id']

    json_file_name = '{}/{}.json'.format(temprory_saving_path, content_id)

    json_file = open(json_file_name, 'wb')
    json_file.write(json.dumps(data).encode())
    json_file.close()
    out_file_name = '{}/{}.msd'.format(temprory_saving_path, content_id)
    final_file_name = '{}/{}.msd'.format(book_saving_path, content_id)

    return json_file_name, out_file_name, final_file_name
