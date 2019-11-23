import os
import subprocess

from log import LogMsg, logger


def execute_process(data, username=None):
    logger.info(LogMsg.START, username)
    print("data={}".format(data))
    arr=['/home/nsm/PycharmProjects/online_library/sample_runnable_code.py']
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
