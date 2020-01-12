import os

from check_permission import get_user_permissions, has_permission_or_not, \
    validate_permissions_and_access
from configs import ADMINISTRATORS
from enums import Permissions, Access_level
from helper import model_to_dict, Http_error, model_basic_dict, \
    populate_basic_data, edit_basic_data, Http_response
from log import LogMsg, logger
from messages import Message
from permission.models import Permission
from infrastructure.schema_validator import schema_validate
from ..constants import PERMISSION_ADD_SCHEMA_PATH, PERMISSION_EDIT_SCHEMA_PATH


def add(data, db_session, username):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session,
                                    'PERMISSION_ADD',
                                    access_level=Access_level.Premium)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    schema_validate(data, PERMISSION_ADD_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)

    if check_permission_exists(data.get('permission'), db_session):
        raise Http_error(409, Message.ALREADY_EXISTS)
    model_instance = Permission()
    populate_basic_data(model_instance, username, data.get('tags'))
    logger.debug(LogMsg.POPULATING_BASIC_DATA)
    model_instance.permission = data.get('permission')
    model_instance.description = data.get('description')
    db_session.add(model_instance)

    logger.info(LogMsg.END)
    return model_instance


def get(id, db_session, username=None):
    logger.info(LogMsg.START, username)
    limited_permissions = False

    logger.debug(LogMsg.PERMISSION_CHECK, username)
    permission_result = validate_permissions_and_access(username, db_session,
                                                        'PERMISSION_GET')
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    access_type = permission_result.get('access_type')
    if access_type == 'Normal':
        logger.error(LogMsg.PERMISSION_DENIED,
                     '{} is a normal_user'.format(username))
        raise Http_error(403, Message.ACCESS_DENIED)

    logger.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(Permission).filter(
        Permission.id == id).first()
    if model_instance:
        logger.debug(LogMsg.GET_SUCCESS,
                     model_to_dict(model_instance))

    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.NOT_FOUND)
    if access_type == 'Press':
        if 'PREMIUM' in model_instance.permission:
            logger.error(LogMsg.PERMISSION_DENIED,
                         {'premium_permission_id': id})
            raise Http_error(403, Message.ACCESS_DENIED)

    logger.info(LogMsg.END)

    return model_instance


def edit(id, db_session, data, username):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session,
                                    'PERMISSION_EDIT',
                                    access_level=Access_level.Premium)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    logger.debug(LogMsg.EDIT_REQUST, {'permission_id': id, 'data': data})
    schema_validate(data, PERMISSION_EDIT_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)

    model_instance = db_session.query(Permission).filter(
        Permission.id == id).first()
    if model_instance:
        logger.debug(LogMsg.MODEL_GETTING)
    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED, {'permission_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    try:
        for key, value in data.items():
            setattr(model_instance, key, value)
        edit_basic_data(model_instance, username, data.get('tags'))

        logger.debug(LogMsg.MODEL_ALTERED,
                     model_to_dict(model_instance))

    except:
        logger.exception(LogMsg.EDIT_FAILED, exc_info=True)
        raise Http_error(409, Message.ALREADY_EXISTS)

    logger.info(LogMsg.END)
    return model_instance


def delete(id, db_session, username):
    logger.info(LogMsg.START, username)

    logger.info(LogMsg.DELETE_REQUEST, {'permission_id': id})
    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session,
                                    'PERMISSION_DELETE',
                                    access_level=Access_level.Premium)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    model_instance = db_session.query(Permission).filter(
        Permission.id == id).first()
    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'permission_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    try:
        db_session.delete(model_instance)

    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(500, LogMsg.DELETE_FAILED)

    logger.info(LogMsg.END)
    return Http_response(204, True)


def get_all(db_session, username):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.PERMISSION_CHECK, username)
    permission_result = validate_permissions_and_access(username, db_session,
                                                        'PERMISSION_GET')
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    access_type = permission_result.get('access_type')
    if access_type == 'Normal':
        logger.error(LogMsg.PERMISSION_DENIED,
                     '{} is a normal_user'.format(username))
        raise Http_error(403, Message.ACCESS_DENIED)

    try:
        result = db_session.query(Permission).all()
        logger.debug(LogMsg.GET_SUCCESS)
    except:
        logger.error(LogMsg.GET_FAILED)
        raise Http_error(500, LogMsg.GET_FAILED)
    final_res = []
    if access_type == 'Press':
        for model in result:
            if not 'PREMIUM' in model.permission:
                final_res.append(model)
        return final_res

    logger.debug(LogMsg.END)
    return result


def search_permission(data, db_session, username=None):
    logger.info(LogMsg.START, username)
    if data.get('sort') is None:
        data['sort'] = ['creation_date-']
    logger.debug(LogMsg.PERMISSION_CHECK, username)
    permission_result = validate_permissions_and_access(username, db_session,
                                                        'PERMISSION_GET')
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    access_type = permission_result.get('access_type')
    if access_type == 'Normal':
        logger.error(LogMsg.PERMISSION_DENIED,
                     '{} is a normal_user'.format(username))
        raise Http_error(403, Message.ACCESS_DENIED)

    result = []
    permissions = Permission.mongoquery(
        db_session.query(Permission)).query(
        **data).end().all()
    if access_type == 'Press':
        for model in permissions:
            if not 'PREMIUM' in model.permission:
                result.append(model_to_dict(model))
        return result

    for permission in permissions:
        result.append(model_to_dict(permission))
    logger.debug(LogMsg.GET_SUCCESS, result)

    logger.info(LogMsg.END)
    return result


def validate_permissions(permission_list, db_session):
    result = db_session.query(Permission).filter(
        Permission.id.in_(set(permission_list))).all()
    if (result is not None) and (len(set(permission_list)) == len(result)):
        return result
    else:
        raise Http_error(404, Message.INVALID_GROUP)


def check_permission_exists(permission, db_session):
    result = db_session.query(Permission).filter(
        Permission.permission == permission).first()
    if result is None:
        return False
    return True


def get_permissions_values(permission_list, db_session):
    result = db_session.query(Permission).filter(
        Permission.id.in_(set(permission_list))).all()
    permission_values = []
    for item in result:
        permission_values.append(item.permission)
    return permission_values


def permission_list(db_session, query_term=None):
    if query_term is None:
        result = db_session.query(Permission).all()
    else:
        result = db_session.query(Permission).filter(
            Permission.permission.like('%{}%'.format(query_term))).all()
    final_res = []
    for item in result:
        final_res.append(item.id)
    return final_res


def permissions_to_db(db_session, username):
    logger.info(LogMsg.START, username)
    if username not in ADMINISTRATORS:
        logger.error(LogMsg.PERMISSION_DENIED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    permissions = Permissions.__members__
    print(permissions)
    result = []
    for permission in permissions:
        if not check_permission_exists(permission, db_session):
            model_instance = Permission()
            populate_basic_data(model_instance, username)
            logger.debug(LogMsg.POPULATING_BASIC_DATA)
            model_instance.permission = permission
            db_session.add(model_instance)
            result.append(model_instance)

    logger.info(LogMsg.END)
    return result
