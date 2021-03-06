import json
import random
from uuid import uuid4

from helper import Http_error, value
from log import LogMsg, logger
from app_redis import app_redis as redis
from repository.person_repo import validate_person
from send_message.send_message import send_message
from infrastructure.schema_validator import schema_validate
from repository.user_repo import check_by_cell_no, check_by_username
from messages import Message
from .constants import REGISTER_SCHEMA_PATH, FORGET_PASS_SCHEMA_PATH, \
    ACTIVATE_ACCOUNT_SCHEMA_PATH

valid_activating_intervall = value('valid_activating_intervall', 86400)
valid_registering_intervall = value('valid_registering_intervall', 200)


def app_ping():
    return {"result": "app is on"}


def activate_account(data, db_session):
    logger.info(LogMsg.START, data)

    schema_validate(data,ACTIVATE_ACCOUNT_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)

    cell_no = data.get('cell_no')

    logger.debug(LogMsg.CHECK_USER_EXISTANCE)
    if check_by_cell_no(cell_no, db_session):
        logger.error(LogMsg.USER_XISTS, data)
        raise Http_error(409, Message.USER_ALREADY_EXISTS)

    logger.debug(LogMsg.CHECK_REDIS_FOR_EXISTANCE)

    cell_data = redis.get(cell_no)
    if cell_data is None:
        logger.error(LogMsg.REGISTER_KEY_DOESNT_EXIST)
        raise Http_error(404, Message.NO_VALID_ACTIVATION_CODE)

    activation_code = (json.loads(cell_data.decode("utf-8"))).get(
        'activation_code', None)
    print(activation_code)

    if activation_code is None:
        logger.error(LogMsg.USER_HAS_SIGNUP_TOKEN)
        raise Http_error(404, Message.NO_VALID_ACTIVATION_CODE)

    if activation_code != data.get('activation_code'):
        logger.error(LogMsg.REGISTER_KEY_INVALID)
        raise Http_error(409, Message.WRONG_ACTIVATION_CODE)

    signup_token = str(uuid4())
    redis.delete(cell_no)
    redis.set(cell_no, json.dumps({'signup_token': signup_token}),
              ex=valid_activating_intervall)

    data = {'cell_no': cell_no, 'signup_token': signup_token}

    return data


def register(data, db_session):
    logger.info(LogMsg.START, data)

    schema_validate(data, REGISTER_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)

    cell_no = data.get('cell_no')

    logger.debug(LogMsg.CHECK_USER_EXISTANCE)

    if check_by_cell_no(cell_no, db_session):
        logger.error(LogMsg.USER_XISTS)
        raise Http_error(409, Message.USER_ALREADY_EXISTS)

    logger.debug(LogMsg.CHECK_REDIS_FOR_EXISTANCE)

    cell_data = redis.get(cell_no)

    if cell_data:
        logger.error(LogMsg.REGISTER_XISTS)
        activation_code = (json.loads(cell_data.decode('utf-8'))).get(
            'activation_code', None)
        if activation_code:
            logger.error(LogMsg.USER_HAS_ACTIVATION_CODE)
            raise Http_error(403, {'msg': Message.ALREADY_HAS_VALID_KEY,
                                   'time': redis.ttl(cell_no)})
        else:
            logger.error(LogMsg.USER_HAS_SIGNUP_TOKEN)
            redis.delete(cell_no)
    logger.debug(LogMsg.GENERATING_REGISTERY_CODE, cell_no)

    password = str(random.randint(1000, 9999))

    data = {'receptor': cell_no,
            'token': password,
            'type': 'sms',
            'template': 'register'}
    logger.debug(LogMsg.SEND_CODE_BY_SMS.format(cell_no))
    sent_data = send_message(data)

    redis.set(cell_no, json.dumps({'activation_code': password}),
              ex=valid_registering_intervall)
    result = {'msg': Message.MESSAGE_SENT, 'cell_no': cell_no,
              'time': redis.ttl(cell_no)}
    logger.debug(LogMsg.SMS_SENT, result)
    logger.info(LogMsg.END)

    return result


def forget_pass(data, db_session):
    logger.info(LogMsg.START, data)

    schema_validate(data, FORGET_PASS_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)

    reset_password_interval = value('reset_password_interval', 120)
    username = data.get('username')
    cell_no = data.get('cell_no')

    user = None
    if username:
        user = check_by_username(username, db_session)
    elif cell_no:
        user = check_by_cell_no(cell_no, db_session)
    else:
        logger.error(LogMsg.INVALID_USER, data)
        raise Http_error(400, Message.USERNAME_CELLNO_REQUIRED)

    if user:
        person = validate_person(user.person_id, db_session)
        logger.debug(LogMsg.PERSON_EXISTS, username)
        password = str(random.randint(1000, 9999))

        sending_data = {'receptor': person.cell_no,
                        'token': user.username,
                        'token2': password,
                        'type': 'sms',
                        'template': 'resetPassword'}
        send_message(sending_data)
        logger.debug(LogMsg.SMS_SENT, sending_data)

        redis_key = 'PASS_{}'.format(person.cell_no)
        redis.set(redis_key, password, ex=reset_password_interval)
        logger.debug(LogMsg.REDIS_SET, redis_key)
        logger.info(LogMsg.END)

        return data
    logger.error(LogMsg.INVALID_USER, data)
    raise Http_error(404, Message.INVALID_USER)
