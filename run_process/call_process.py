import subprocess

from log import LogMsg, logger



def execute_process(data,db_session,username=None):
    logger.info(LogMsg.START,username)

    DETACHED_PROCESS = 0x00000008
    results = subprocess.Popen(['/usr/bin/python','/home/nsm/process_to_call'], close_fds=True, stdout=subprocess.PIPE)
    streamdata = results.communicate()[0]

    res = results.stdout.read()
    print(res)

    return streamdata

