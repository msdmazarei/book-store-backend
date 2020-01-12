from check_permission import get_user_permissions, has_permission_or_not, \
    has_permission, validate_permissions_and_access
from configs import ADMINISTRATORS
from enums import Permissions, Access_level
from helper import model_to_dict, Http_error, populate_basic_data, \
    Http_response, model_basic_dict
from log import LogMsg, logger
from messages import Message
from permission.controllers.permission import validate_permissions, \
    permission_list
from repository.group_repo import validate_groups, validate_group
from infrastructure.schema_validator import schema_validate
from repository.group_user_repo import user_is_in_group
from repository.user_repo import check_user
from ..models import GroupPermission
from ..constants import GROUP_ADD_SCHEMA_PATH, A_GROUP_ADD_SCHEMA_PATH
from group.controllers.group import get as get_group
from .permission import get as get_permission


def add(permission_id, group_id, db_session, username):
    logger.info(LogMsg.START, username)

    user = check_user(username, db_session)
    group = get_group(group_id, db_session, username=None)
    permission = get_permission(permission_id, db_session)
    if user.person_id != group.person_id:
        logger.error(LogMsg.PERMISSION_DENIED,
                     {'add_permission_to_group_be user': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    if group_has_permission(permission_id, group_id, db_session):
        logger.error(LogMsg.PERMISSION_GROUP_ALREADY_HAS)
        raise Http_error(409, Message.ALREADY_EXISTS)

    permissions, presses = get_user_permissions(username, db_session)

    if permission.permission not in permissions:
        logger.error(LogMsg.PREMIUM_PERMISSION_ADDITION_RESTRICTION,
                     username)
        raise Http_error(403, Message.ACCESS_DENIED)

    model_instance = GroupPermission()
    populate_basic_data(model_instance, username)
    logger.debug(LogMsg.POPULATING_BASIC_DATA)
    model_instance.group_id = group_id
    model_instance.permission_id = permission_id

    db_session.add(model_instance)

    logger.info(LogMsg.END)
    return model_instance


def get(id, db_session, username=None):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.MODEL_GETTING)

    model_instance = db_session.query(GroupPermission).filter(
        GroupPermission.id == id).first()

    if model_instance:
        logger.debug(LogMsg.GET_SUCCESS,
                     model_to_dict(model_instance))
    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.NOT_FOUND)

    if username is not None:
        user = check_user(username, db_session)
        per_data = {}
        if user_is_in_group(user.id, model_instance.group_id,
                            db_session):
            per_data.update({Permissions.IS_MEMBER.value: True})

        logger.debug(LogMsg.PERMISSION_CHECK, username)
        validate_permissions_and_access(username, db_session,
                                        'GROUP_PERMISSION_GET', per_data)
        logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    logger.info(LogMsg.END)

    return group_permission_to_dict(model_instance)


def delete(id, db_session, username):
    logger.info(LogMsg.START, username)

    logger.info(LogMsg.DELETE_REQUEST, {'group_permission_id': id})

    model_instance = db_session.query(GroupPermission).filter(
        GroupPermission.id == id).first()
    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'group_permission_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    group = get_group(model_instance.group_id, db_session, username=None)

    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session,
                                    'GROUP_PERMISSION_DELETE', model=group,
                                    access_level=Access_level.Premium)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    try:
        db_session.delete(model_instance)
    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(500, LogMsg.DELETE_FAILED)

    logger.info(LogMsg.END)

    return Http_response(204, True)


def get_all(data, db_session, username):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session,
                                    'GROUP_PERMISSION_GET',
                                    access_level=Access_level.Premium)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    if data.get('sort') is None:
        data['sort'] = ['creation_date-']

    try:
        result = GroupPermission.mongoquery(
            db_session.query(GroupPermission)).query(
            **data).end().all()
        logger.debug(LogMsg.GET_SUCCESS)
        final_res = []
        for item in result:
            final_res.append(group_permission_to_dict(item))
    except:
        logger.error(LogMsg.GET_FAILED)
        raise Http_error(500, LogMsg.GET_FAILED)

    logger.info(LogMsg.END)
    return final_res


def group_has_permission(permission_id, group_id, db_session):
    result = db_session.query(GroupPermission).filter(
        GroupPermission.permission_id == permission_id,
        GroupPermission.group_id == group_id).first()
    if result is None:
        return False
    return True


def delete_permission_for_group(permission_id, group_id, db_session):
    db_session.query(GroupPermission).filter(
        GroupPermission.permission_id == permission_id,
        GroupPermission.group_id == group_id).delete()
    return True


def add_permissions_to_groups(data, db_session, username):
    logger.info(LogMsg.START, username)

    schema_validate(data, GROUP_ADD_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)

    permissions = set(data.get('permissions'))
    groups = set(data.get('groups'))

    validate_permissions(permissions, db_session)
    validate_groups(groups, db_session)
    final_res = {}
    for group_id in groups:
        result = []

        for permission_id in permissions:
            if group_has_permission(permission_id, group_id, db_session):
                logger.error(LogMsg.PERMISSION_GROUP_ALREADY_HAS,
                             {'permission_id': permission_id,
                              'group_id': group_id})
                raise Http_error(409, Message.ALREADY_EXISTS)
            result.append(group_permission_to_dict(
                add(permission_id, group_id, db_session, username)))
        final_res.update({group_id: result})

    logger.info(LogMsg.END)
    return final_res


def delete_permissions_of_groups(data, db_session, username):
    logger.info(LogMsg.START, username)

    schema_validate(data, GROUP_ADD_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)

    permissions = set(data.get('permissions'))
    groups = set(data.get('groups'))

    validate_permissions(permissions, db_session)
    validate_groups(groups, db_session)
    for group_id in groups:
        group = get_group(group_id, db_session, username)
        logger.debug(LogMsg.PERMISSION_CHECK, username)
        validate_permissions_and_access(username, db_session,
                                        'GROUP_PERMISSION_DELETE', model=group,
                                        access_level=Access_level.Premium)
        logger.debug(LogMsg.PERMISSION_VERIFIED, username)

        for permission_id in permissions:
            if not group_has_permission(permission_id, group_id, db_session):
                logger.error(LogMsg.PERMISSION_NOT_HAS_GROUP,
                             {'permission_id': permission_id,
                              'group_id': group_id})
                raise Http_error(404, Message.PERMISSION_NOT_FOUND)
            delete_permission_for_group(permission_id, group_id, db_session)

    logger.info(LogMsg.END)
    return {'result': 'successful'}


def add_group_permissions(data, db_session, username):
    logger.info(LogMsg.START, username)

    schema_validate(data, A_GROUP_ADD_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)

    group_id = data.get('group_id')
    permissions = data.get('permissions')

    validate_group(group_id, db_session)
    result = []
    for permission_id in permissions:
        if group_has_permission(permission_id, group_id, db_session):
            logger.error(LogMsg.GROUP_USER_IS_IN_GROUP,
                         {'permission_id': permission_id, 'group_id': group_id})
            raise Http_error(409, Message.ALREADY_EXISTS)
        result.append(
            group_permission_to_dict(
                add(permission_id, group_id, db_session, username)))

    logger.info(LogMsg.END)
    return result


def delete_group_permissions(data, db_session, username):
    logger.info(LogMsg.START, username)

    schema_validate(data, A_GROUP_ADD_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)

    group_id = data.get('group_id')
    permissions = data.get('permissions')


    group = get_group(group_id, db_session, username)
    if group is None:
        logger.error(LogMsg.NOT_FOUND,{'group_id':group_id})
        raise Http_error(404,Message.NOT_FOUND)

    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session,
                                    'GROUP_PERMISSION_DELETE', model=group,
                                    access_level=Access_level.Premium)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    result = []
    for permission_id in permissions:
        if not group_has_permission(permission_id, group_id, db_session):
            logger.error(LogMsg.PERMISSION_NOT_HAS_GROUP,
                         {'permission_id': permission_id, 'group_id': group_id})
            raise Http_error(404, Message.PERMISSION_NOT_FOUND)
        delete_permission_for_group(permission_id, group_id, db_session,
                                    username)

    logger.info(LogMsg.END)
    return result


def get_by_data(data, db_session, username):
    logger.info(LogMsg.START, username)
    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session,
                                    'GROUP_PERMISSION_GET',
                                    access_level=Access_level.Premium)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    if data.get('sort') is None:
        data['sort'] = ['creation_date-']

    result = []
    permissions = GroupPermission.mongoquery(
        db_session.query(GroupPermission)).query(
        **data).end().all()
    for permission in permissions:
        result.append(group_permission_to_dict(permission))
    logger.debug(LogMsg.GET_SUCCESS, result)

    logger.info(LogMsg.END)
    return result


def get_by_permission(permission_id, db_session, username):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session,
                                    'GROUP_PERMISSION_GET',
                                    access_level=Access_level.Premium)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    result = db_session.query(GroupPermission).filter(
        GroupPermission.permission_id == permission_id).all()
    final_res = []
    for item in result:
        final_res.append(group_permission_to_dict(item))
    logger.info(LogMsg.END)
    return final_res


def delete_all_permissions_of_group(group_id, db_session):
    db_session.query(GroupPermission).filter(
        GroupPermission.group_id == group_id).delete()
    return True


def get_permission_list_of_groups(group_list, db_session):
    groups = set(group_list)
    result = db_session.query(GroupPermission).filter(
        GroupPermission.group_id.in_(groups)).all()

    permissions = []
    for item in result:
        permissions.append(str(item.permission_id))
    return set(permissions)


def group_permission_list(data, db_session, username):
    logger.info(LogMsg.START, username)
    groups = data.get('groups', None)
    result = db_session.query(GroupPermission).filter(
        GroupPermission.group_id.in_(groups)).all()

    permissions = []
    for item in result:
        if has_get_permission(username,item.group_id,db_session,'GROUP_PERMISSION_GET'):
            permissions.append(group_permission_to_dict(item))
    logger.info(LogMsg.END)
    return permissions


def premium_permission_group(group_id, db_session, username):
    logger.info(LogMsg.START,username)
    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session,
                                    'ASSIGN_PREMIUM_PERMISSION_GROUP',
                                    access_level=Access_level.Premium)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    permissions = permission_list(db_session, 'PREMIUM')
    result = []
    for permission_id in permissions:
        if group_has_permission(permission_id, group_id, db_session):
            logger.debug(LogMsg.PERMISSION_GROUP_ALREADY_HAS)
            pass
        else:
            model_instance = GroupPermission()
            populate_basic_data(model_instance, username)
            logger.debug(LogMsg.POPULATING_BASIC_DATA)
            model_instance.group_id = group_id
            model_instance.permission_id = permission_id
            db_session.add(model_instance)
            result.append(group_permission_to_dict(model_instance))
    logger.info(LogMsg.END)
    return result


def group_permission_to_dict(model_instance):
    result = {
        'group_id': model_instance.group_id,
        'permission_id': model_instance.permission_id,
        'permission': model_to_dict(model_instance.permission)
    }
    primary_data = model_basic_dict(model_instance)
    result.update(primary_data)
    return result



def has_get_permission(username,group_id,db_session,func_name):
    user = check_user(username,db_session)
    permission = '{}_PREMIUM'.format(func_name)
    permissions,presses = get_user_permissions(username,db_session)
    if user_is_in_group(user.id,group_id,db_session) :
        return True
    elif username in ADMINISTRATORS:
        return True
    elif permission in permissions:
        return True
    return False