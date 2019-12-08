from check_permission import get_user_permissions, has_permission
from enums import Permissions
from helper import Http_error, value, populate_basic_data, edit_basic_data, \
    model_to_dict, Http_response, check_schema
from log import LogMsg, logger
from messages import Message
from repository.user_repo import check_user
from ..models import DeviceCode
from random import randint
from base64 import b64encode

active_device_per_user = value('active_device_per_user', None)
if active_device_per_user is None:
    logger.error(LogMsg.APP_CONFIG_INCORRECT, {'active_device_per_user': None})
    raise Http_error(500, Message.APP_CONFIG_MISSING)


def add(data, db_session, username):
    logger.info(LogMsg.START, username)

    check_schema(['name'], data.keys())

    user = check_user(username, db_session)
    if user is None:
        logger.error(LogMsg.INVALID_USER, username)
        raise Http_error(404, Message.INVALID_USER)
    user_id = user.id
    if 'user_id' in data.keys():
        user_id = data.get('user_id')

    per_data = {}
    permissions, presses = get_user_permissions(username, db_session)
    if user.id == user_id:
        per_data.update({Permissions.IS_OWNER.value: True})
    has_permission([Permissions.DEVICE_KEY_ADD_PREMIUM],
                   permissions, None, per_data)
    logger.debug(LogMsg.PERMISSION_VERIFIED)

    devices = get_user_active_devices(user_id, db_session)

    if not devices < int(active_device_per_user):
        logger.error(LogMsg.MAXIMUM_ACTIVE_DEVICE, devices)
        raise Http_error(409, Message.MAXIMUM_ACTIVE_DEVICE)

    device_key = DeviceCode()
    populate_basic_data(device_key, username, data.get('tags'))
    logger.debug(LogMsg.POPULATING_BASIC_DATA)
    device_key.user_id = user_id
    device_key.code = build_device_encription_code()
    device_key.name = data.get('name')
    db_session.add(device_key)
    logger.debug(LogMsg.DB_ADD)
    logger.info(LogMsg.END)
    return device_key


def get_user_active_devices(user_id, db_session):
    logger.info(LogMsg.START, '')
    device_count = db_session.query(DeviceCode).filter(
        DeviceCode.user_id == user_id).count()
    logger.debug(LogMsg.USER_DEVICE_COUNT,
                 {'user_id': user_id, 'device_count': device_count})
    logger.info(LogMsg.END)
    return device_count


def build_device_encription_code():
    logger.info(LogMsg.START, '')
    code = ''
    for i in range(0, 1000):
        random_char = chr(randint(0, 255))
        code = '{}{}'.format(code, random_char)
    encription_key = b64encode(code.encode()).decode()
    return encription_key


def get(id, db_session, username):
    logger.info(LogMsg.START, username)

    user = check_user(username, db_session)

    model_instance = db_session.query(DeviceCode).filter(
        DeviceCode.id == id).first()
    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'device_key': id})
        raise Http_error(404, Message.NOT_FOUND)
    result = model_to_dict(model_instance)
    logger.debug(LogMsg.GET_SUCCESS, result)

    per_data = {}
    permissions, presses = get_user_permissions(username, db_session)
    if model_instance.user_id == user.id:
        per_data.update({Permissions.IS_OWNER.value: True})
    has_permission([Permissions.DEVICE_KEY_GET_PREMIUM],
                   permissions, None, per_data)

    logger.debug(LogMsg.PERMISSION_VERIFIED)

    logger.info(LogMsg.END)
    return result


def get_user_devices(user_id, db_session, username):
    logger.info(LogMsg.START, username)

    user = check_user(username, db_session)

    logger.debug(LogMsg.PERMISSION_CHECK,
                 {username: Permissions.DEVICE_KEY_GET_PREMIUM})
    per_data = {}
    permissions, presses = get_user_permissions(username, db_session)
    if user_id == user.id:
        per_data.update({Permissions.IS_OWNER.value: True})
    has_permission([Permissions.DEVICE_KEY_GET_PREMIUM],
                   permissions, None, per_data)
    logger.debug(LogMsg.PERMISSION_VERIFIED)

    result = db_session.query(DeviceCode).filter(
        DeviceCode.user_id == user_id).all().order_by(DeviceCode.creation_date.desc())
    final_res = []
    for item in result:
        final_res.append(model_to_dict(item))
    logger.debug(LogMsg.GET_SUCCESS, final_res)
    logger.info(LogMsg.END)
    return final_res


def delete(id, db_session, username):
    logger.info(LogMsg.START, username)

    user = check_user(username, db_session)

    model_instance = db_session.query(DeviceCode).filter(
        DeviceCode.id == id).first()
    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'device_key': id})
        raise Http_error(404, Message.NOT_FOUND)
    result = model_to_dict(model_instance)
    logger.debug(LogMsg.GET_SUCCESS, result)

    per_data = {}
    permissions, presses = get_user_permissions(username, db_session)
    if model_instance.user_id == user.id:
        per_data.update({Permissions.IS_OWNER.value: True})
    has_permission([Permissions.DEVICE_KEY_DELETE_PREMIUM],
                   permissions, None, per_data)

    logger.debug(LogMsg.PERMISSION_VERIFIED)

    try:
        db_session.delete(model_instance)
        logger.debug(LogMsg.DELETE_SUCCESS, {'device_key_id'})
    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(500, Message.DELETE_FAILED)

    logger.info(LogMsg.END)
    return Http_response(204, True)


def get_all(data, db_session, username):
    logger.info(LogMsg.START, username)

    permissions, presses = get_user_permissions(username, db_session)

    has_permission([Permissions.DEVICE_KEY_GET_PREMIUM], permissions)

    logger.debug(LogMsg.PERMISSION_VERIFIED)

    if data.get('sort') is None:
        data['sort'] = ['creation_date-']

    if data is None:
        result = db_session.query(DeviceCode).all()
    else:
        result = DeviceCode.mongoquery(db_session.query(DeviceCode)).query(
            **data).end().all()

    final_res = []
    for device_key in result:
        final_res.append(model_to_dict(device_key))
    logger.info(LogMsg.END)
    return final_res


def user_device_exist(user_id, device_id, db_session):
    result = db_session.query(DeviceCode).filter(DeviceCode.user_id == user_id,
                                                 DeviceCode.id == device_id).first()
    if result is None:
        return False
    return True
