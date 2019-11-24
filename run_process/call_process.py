import os
import subprocess

from helper import value, Http_error
from log import LogMsg, logger
from messages import Message

book_generator_app_address = value('book_generator_app_address',None)
if book_generator_app_address is None:
    logger.error(LogMsg.APP_CONFIG_INCORRECT,{'book_generator_app_address':None
                                              })
    raise Http_error(500,Message.APP_CONFIG_MISSING)

def execute_process(data, username=None):
    logger.info(LogMsg.START, username)
    logger.debug(LogMsg.RUN_PROCESS_DATA,data)

    print("data={}".format(data))
    arr=[book_generator_app_address]
    arr.extend(data)
    results = subprocess.Popen(
        arr,
        close_fds=True, stdout=subprocess.PIPE)
    streamdata = results.communicate()[0]
    if results.returncode != 0:
        error = results.stderr
        logger.error(LogMsg.BOOK_GENERATE_FAILED,error)
        os.remove(data[0])
        os.remove(data[1])
        os.close()
        raise Exception('process failed.')
    print(results)
    logger.info(LogMsg.END)
    return results.__dict__
