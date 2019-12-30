import os

from check_permission import get_user_permissions, has_permission_or_not, \
    has_permission
from configs import ADMINISTRATORS
from enums import Permissions
from helper import model_to_dict, Http_error, model_basic_dict, \
    populate_basic_data, Http_response
from infrastructure.schema_validator import schema_validate
from log import LogMsg, logger
from messages import Message
from repository.group_repo import validate_groups, validate_group, \
    check_group_title_exists, groups_by_presses
from repository.group_user_repo import users_of_groups
from repository.person_repo import get_persons
from repository.user_repo import validate_users, check_user, persons_by_user
from .group import add as add_group
from ..models import GroupUser
from ..constants import USER_ADD_SCHEMA_PATH, USER_GROUP_SCHEMA_PATH

save_path = os.environ.get('save_path')


def add(user_id, group_id, db_session, username):
    logger.info(LogMsg.START, username)

    if user_is_in_group(user_id, group_id, db_session):
        logger.error(LogMsg.GROUP_USER_IS_IN_GROUP)
        raise Http_error(409, Message.ALREADY_EXISTS)

    model_instance = GroupUser()
    populate_basic_data(model_instance, username)
    logger.debug(LogMsg.POPULATING_BASIC_DATA)
    model_instance.group_id = group_id
    model_instance.user_id = user_id

    db_session.add(model_instance)

    logger.info(LogMsg.END)
    return model_instance


def get(id, db_session, username=None):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(GroupUser).filter(
        GroupUser.id == id).first()
    if model_instance:
        logger.debug(LogMsg.GET_SUCCESS,
                     model_to_dict(model_instance))
    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.NOT_FOUND)
    logger.error(LogMsg.GET_FAILED, {"id": id})
    logger.info(LogMsg.END)

    return group_user_to_dict(model_instance)


def delete(id, db_session, username):
    logger.info(LogMsg.START, username)
    user = check_user(username,db_session)

    logger.info(LogMsg.DELETE_REQUEST, {'group_user_id': id})
    # if username not in ADMINISTRATORS:
    #     logger.error(LogMsg.NOT_ACCESSED, {'username': username})
    #     raise Http_error(403, Message.ACCESS_DENIED)
    model_instance = db_session.query(GroupUser).filter(
        GroupUser.id == id).first()

    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'group_user_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    permissions, presses = get_user_permissions(username, db_session)

    permit = has_permission_or_not([Permissions.PERMISSION_GROUP_USER_DELETE_PREMIUM],
                                   permissions)
    if not permit:
        press_permit = has_permission_or_not(
            [Permissions.PERMISSION_GROUP_USER_DELETE_PRESS],
            permissions)
        if not (press_permit and (model_instance.group.person_id == user.person_id)):
            logger.error(LogMsg.PERMISSION_DENIED,
                         {'PERMISSION_GROUP_USER_DELETE': username})
            raise Http_error(403, Message.ACCESS_DENIED)


    try:
        db_session.delete(model_instance)
    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(500, LogMsg.DELETE_FAILED)

    logger.info(LogMsg.END)

    return Http_response(204, True)


def get_all(data, db_session, username):
    logger.info(LogMsg.START, username)
    permissions, presses = get_user_permissions(username, db_session)

    has_permission(
        [Permissions.PERMISSION_GROUP_USER_GET_PREMIUM],
        permissions)

    if data.get('sort') is None:
        data['sort'] = ['creation_date-']

    try:
        result = GroupUser.mongoquery(db_session.query(GroupUser)).query(
            **data).end().all()
        logger.debug(LogMsg.GET_SUCCESS)
        final_res = []
        for item in result:
            final_res.append(group_user_to_dict(item))
    except:
        logger.error(LogMsg.GET_FAILED)
        raise Http_error(500, LogMsg.GET_FAILED)

    logger.debug(LogMsg.END)
    return final_res


def user_is_in_group(user_id, group_id, db_session):
    result = db_session.query(GroupUser).filter(GroupUser.user_id == user_id,
                                                GroupUser.group_id == group_id).first()
    if result is None:
        return False
    return True


def delete_user_group(user_id, group_id, db_session):
    db_session.query(GroupUser).filter(GroupUser.user_id == user_id,
                                       GroupUser.group_id == group_id).delete()

    return True


def add_users_to_groups(data, db_session, username):
    logger.info(LogMsg.START, username)
    user = check_user(username,db_session)

    # if username not in ADMINISTRATORS:
    #     logger.error(LogMsg.NOT_ACCESSED, {'username': username})
    #     raise Http_error(403, Message.ACCESS_DENIED)


    schema_validate(data,USER_ADD_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)

    users = set(data.get('users'))
    groups = set(data.get('groups'))


    validate_users(users, db_session)
    group_entities = validate_groups(groups, db_session)


    permissions, presses = get_user_permissions(username, db_session)

    permit = has_permission_or_not([Permissions.PERMISSION_GROUP_USER_ADD_PREMIUM],
                                   permissions)
    if not permit:
        press_permit = has_permission_or_not(
            [Permissions.PERMISSION_GROUP_USER_ADD_PRESS],
            permissions)

        if not (press_permit and is_user_group_owner(user.person_id, group_entities)):
            logger.error(LogMsg.PERMISSION_DENIED,
                         {'PERMISSION_GROUP_USER_ADD': username})
            raise Http_error(403, Message.ACCESS_DENIED)

    final_res = {}
    for group_id in groups:
        result = []
        for user_id in users:
            if user_is_in_group(user_id, group_id, db_session):
                logger.error(LogMsg.GROUP_USER_IS_IN_GROUP,
                             {'user_id': user_id, 'group_id': group_id})
                raise Http_error(409, Message.ALREADY_EXISTS)
            result.append(
                model_to_dict(add(user_id, group_id, db_session, username)))
        final_res.update({group_id: result})

    logger.info(LogMsg.END)
    return final_res


def delete_users_from_groups(data, db_session, username):
    logger.info(LogMsg.START, username)

    user = check_user(username,db_session)

    schema_validate(data,USER_ADD_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)

    users = set(data.get('users'))
    groups = set(data.get('groups'))

    validate_users(users, db_session)
    group_entities = validate_groups(groups, db_session)



    permissions, presses = get_user_permissions(username, db_session)

    permit = has_permission_or_not([Permissions.PERMISSION_GROUP_USER_DELETE_PREMIUM],
                                   permissions)
    if not permit:
        press_permit = has_permission_or_not(
            [Permissions.PERMISSION_GROUP_USER_DELETE_PRESS],
            permissions)

        if not (press_permit and is_user_group_owner(user.person_id, group_entities)):
            logger.error(LogMsg.PERMISSION_DENIED,
                         {'PERMISSION_GROUP_USER_ADD': username})
            raise Http_error(403, Message.ACCESS_DENIED)

    for group_id in groups:
        for user_id in users:
            if not user_is_in_group(user_id, group_id, db_session):
                logger.error(LogMsg.GROUP_USER_NOT_IN_GROUP,
                             {'user_id': user_id, 'group_id': group_id})
                raise Http_error(404, Message.NOT_IN_GROUP)
            delete_user_group(user_id, group_id, db_session)

    logger.info(LogMsg.END)
    return {'result': 'successful'}


def add_group_users(data, db_session, username):
    logger.info(LogMsg.START, username)
    user = check_user(username,db_session)

    schema_validate(data,USER_GROUP_SCHEMA_PATH)

    group_id = data.get('group_id')

    users = data.get('users')

    group = validate_group(group_id, db_session)


    permissions, presses = get_user_permissions(username, db_session)

    permit = has_permission_or_not([Permissions.PERMISSION_GROUP_USER_ADD_PREMIUM],
                                   permissions)
    if not permit:
        press_permit = has_permission_or_not(
            [Permissions.PERMISSION_GROUP_USER_ADD_PRESS],
            permissions)

        if not (press_permit and is_user_group_owner(user.person_id, [group])):
            logger.error(LogMsg.PERMISSION_DENIED,
                         {'PERMISSION_GROUP_USER_ADD': username})
            raise Http_error(403, Message.ACCESS_DENIED)

    result = []
    for user_id in users:
        if user_is_in_group(user_id, group_id, db_session):
            logger.error(LogMsg.GROUP_USER_IS_IN_GROUP,
                         {'user_id': user_id, 'group_id': group_id})
            raise Http_error(409, Message.ALREADY_EXISTS)
        result.append(add(user_id, group_id, db_session, username))
    final_res = []
    for item in result:
        final_res.append(group_user_to_dict(item))

    logger.info(LogMsg.END)
    return final_res


def get_by_group(group_id, db_session, username):
    logger.info(LogMsg.START, username)

    user = check_user(username,db_session)
    group = validate_group(group_id, db_session)
    permissions, presses = get_user_permissions(username, db_session)

    permit = has_permission_or_not([Permissions.PERMISSION_GROUP_USER_GET_PREMIUM],
                                   permissions)
    if not permit:
        press_permit = has_permission_or_not(
            [Permissions.PERMISSION_GROUP_USER_GET_PRESS],
            permissions)

        if not (press_permit and user_is_in_group(user.id, group_id, db_session)):
            logger.error(LogMsg.PERMISSION_DENIED,
                         {'PERMISSION_GROUP_USER_GET': username})
            raise Http_error(403, Message.ACCESS_DENIED)


    result = db_session.query(GroupUser).filter(
        GroupUser.group_id == group_id).all()
    final_res = []
    for item in result:
        final_res.append(group_user_to_dict(item))
    logger.info(LogMsg.END)
    return final_res


def get_user_groups(user_id, db_session, username):
    logger.info(LogMsg.START, username)

    result = db_session.query(GroupUser).filter(
        GroupUser.user_id == user_id).all()
    final_res = []
    for item in result:
        final_res.append(group_user_to_dict(item))
    logger.info(LogMsg.END)
    return final_res


def add_group_by_users(data, db_session, username):
    logger.info(LogMsg.START, username)

    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    users = set(data.get('users'))
    group_title = data.get('title')
    person_id = data.get('person_id')

    validate_users(users, db_session)
    if check_group_title_exists(group_title, db_session):
        logger.error(LogMsg.GROUP_EXISTS, {'group_title': group_title})
        raise Http_error(409, Message.ALREADY_EXISTS)

    group = add_group({'title': group_title,'person_id':person_id}, db_session, username)
    del data['title']
    data['group_id'] = group.id
    result = add_group_users(data, db_session, username)

    return result


def group_user_to_dict(model_instance):
    result = {
        'group_id': model_instance.group_id,
        'user_id': model_instance.user_id,
        'group': model_to_dict(model_instance.group)
    }
    primary_data = model_basic_dict(model_instance)
    result.update(primary_data)
    return result


def is_user_group_owner(person_id,groups):
    for item in groups:
        if person_id !=item.person_id:
            logger.error(LogMsg.PERMISSION_DENIED,{'group_press_is_not_person':person_id})
            raise Http_error(403,Message.ACCESS_DENIED)
    return True


def press_persons(data,db_session,username):
    logger.info(LogMsg.START,username)
    press_list = data.get('presses')
    groups = groups_by_presses(press_list, db_session)
    users = users_of_groups(groups,db_session)
    person_ids = persons_by_user(users,db_session)
    persons = get_persons(person_ids,db_session)
    return persons