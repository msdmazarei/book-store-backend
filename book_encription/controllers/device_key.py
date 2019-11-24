from helper import Http_error, value
from log import LogMsg, logger
from messages import Message
from repository.user_repo import check_user
from ..models import DeviceCode


active_device_per_user = value('active_device_per_user',None)
if active_device_per_user is None:
    logger.error(LogMsg.APP_CONFIG_INCORRECT,{'active_device_per_user':None})
    raise Http_error(500,Message.APP_CONFIG_MISSING)


def add(data,db_session,username):

    logger.info(LogMsg.START,username)

    user = check_user(username)
    if user is None:
        logger.error(LogMsg.INVALID_USER,username)
        raise Http_error(404,Message.INVALID_USER)
    user_id = user.id
    if 'user_id' in data.keys():
        user_id = data.get('user_id')

    devices = get_user_active_devices(user_id,db_session)

    if not devices<active_device_per_user:
        logger.error(LogMsg.MAXIMUM_ACTIVE_DEVICE,devices)
        raise Http_error(409,Message.MAXIMUM_ACTIVE_DEVICE)

    device_key = DeviceCode()
    


def get_user_active_devices(user_id,db_session):
    logger.info(LogMsg.START,'')
    device_count = db_session.query(DeviceCode).filter(DeviceCode.user_id==user_id).count()
    logger.debug(LogMsg.USER_DEVICE_COUNT,{'user_id':user_id,'device_count':device_count})
    logger.info(LogMsg.END)
    return device_count