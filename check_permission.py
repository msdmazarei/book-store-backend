import json

from books.models import Book, BookContent
from configs import ADMINISTRATORS
from enums import Permissions, Access_level
from helper import Http_error, value
from log import logger, LogMsg
from messages import Message
from repository.group_permission import \
    get_permission_list_of_groups
from repository.group_repo import groups_by_press
from repository.permission_repo import get_permissions_values
from repository.group_user_repo import get_user_group_list, \
    user_is_in_group_list
from repository.user_repo import check_user
from app_redis import app_redis

permission_list_expiration_time = value('permission_list_expiration_time', 30)


def has_permission(func_permissions, user_permission_list, model_instance=None,
                   data=None):
    if any(permission.value in user_permission_list for permission in
           func_permissions):

        return True
    elif data is not None and data.get(Permissions.IS_OWNER.value,
                                       False) is True:
        return True
    logger.error(LogMsg.NOT_ACCESSED, {'permission': 'not_found'})
    logger.error(LogMsg.PERMISSION_DENIED)
    raise Http_error(403, Message.ACCESS_DENIED)


def has_permission_or_not(func_permissions, user_permission_list,
                          model_instance=None,
                          data=None):
    if any(permission.value in user_permission_list for permission in
           func_permissions):
        return True
    elif data is not None:
        if data.get(Permissions.IS_OWNER.value, False) is True:
            return True
        elif data.get(Permissions.IS_MEMBER.value, False) is True:
            return True
    logger.error(LogMsg.NOT_ACCESSED, {'permission': 'not_found'})
    logger.error(LogMsg.PERMISSION_DENIED)
    return False


def get_user_permissions(username, db_session):
    user = check_user(username, db_session)

    if user is None:
        logger.error(LogMsg.NOT_FOUND, {'username': username})
        raise Http_error(404, Message.INVALID_USERNAME)
    redis_key = 'PERMISSIONS_{}'.format(user.id)
    permission_list = app_redis.get(redis_key)
    if permission_list is not None:
        data = json.loads(permission_list.decode("utf-8"))
        return data.get('permission_values', None), data.get('presses', None)

    group_list = get_user_group_list(user.id, db_session)
    if not bool(group_list):
        return [], []
    permissions = get_permission_list_of_groups(group_list.keys(), db_session)
    permission_values = get_permissions_values(permissions, db_session)

    app_redis.set(redis_key, json.dumps({'permission_values': permission_values,
                                         'presses': list(group_list.values())}),
                  ex=permission_list_expiration_time)

    return permission_values, list(group_list.values())


def validate_permissions_and_access(username, db_session, func_name,
                                    special_data=None, model=None,
                                    access_level=None):
    access_type = 'ADMIN'
    premium_requirements = ['{}_PREMIUM'.format(func_name)]
    press_requirements = ['{}_PRESS'.format(func_name)]

    user  = check_user(username,db_session)

    if access_level is not None:
        if access_level == Access_level.Premium:
            press_requirements = []
    if username not in ADMINISTRATORS:
        access_type = 'PREMIUM'
        permissions, presses = get_user_permissions(username, db_session)

        if model is not None:
            if model.creator == username:
                special_data.update({
                    Permissions.IS_OWNER.value: True})
                access_type = 'CREATOR'
            if hasattr(model,'person_id') and model.person_id == user.person_id:
                special_data.update({
                    Permissions.IS_OWNER.value: True})
                access_type = 'OWNER'


        permit = has_permission_or_not(premium_requirements, permissions,
                                       None, special_data)
        if not permit :
            if access_level!=Access_level.Premium:

                logger.debug(LogMsg.PREMIUM_PERMISSION_NOT_FOUND,
                             {'permission': func_name, 'username': username})

                if model is not None and isinstance(model, BookContent):
                    if model.book_press in presses:
                        press_group_ids = groups_by_press(model.book_press,
                                                          db_session)
                        user_groups = user_is_in_group_list(user.id,
                                                            press_group_ids,
                                                            db_session)

                        press_permissions = get_permission_list_of_groups(
                            user_groups, db_session)
                        permission_values = get_permissions_values(
                            press_permissions,
                            db_session)
                        if press_requirements in permission_values:
                            special_data.update({
                                Permissions.IS_OWNER.value: True})
                            access_type = 'Press'
                        else:
                            logger.error(LogMsg.PERMISSION_DENIED,
                                         {'PERMISSION': {
                                             'premium_requirements': premium_requirements,
                                             'press_requirement': press_requirements},
                                             'username': username})
                            raise Http_error(403, Message.ACCESS_DENIED)

                elif model is not None and isinstance(model, Book):
                    if model.press in presses:
                        press_group_ids = groups_by_press(model.press,
                                                          db_session)
                        user_groups = user_is_in_group_list(user.id,
                                                            press_group_ids,
                                                            db_session)

                        press_permissions = get_permission_list_of_groups(
                            user_groups, db_session)
                        permission_values = get_permissions_values(
                            press_permissions,
                            db_session)
                        if press_requirements in permission_values:
                            special_data.update({
                                Permissions.IS_OWNER.value: True})
                            access_type = 'Press'
                        else:
                            logger.error(LogMsg.PERMISSION_DENIED,
                                         {'PERMISSION': {
                                             'premium_requirements': premium_requirements,
                                             'press_requirement': press_requirements},
                                             'username': username})
                            raise Http_error(403, Message.ACCESS_DENIED)

                else:
                    press_permit = has_permission_or_not(press_requirements,
                                                     permissions)
                    access_type = 'Press'
                    membership = special_data.get(Permissions.IS_MEMBER.value,None)
                    if membership is not None :
                        if not(press_permit and membership):
                            logger.error(LogMsg.PERMISSION_DENIED,
                                         {'PERMISSION': {
                                             'premium_requirements': premium_requirements,
                                             'press_requirement': press_requirements},
                                             'membership':membership,
                                             'username': username})
                            raise Http_error(403, Message.ACCESS_DENIED)

                    if not press_permit:
                        logger.error(LogMsg.PERMISSION_DENIED,
                                     {'PERMISSION': {
                                         'premium_requirements': premium_requirements,
                                         'press_requirement': press_requirements},
                                         'username': username})
                        raise Http_error(403, Message.ACCESS_DENIED)
            else:
                logger.error(LogMsg.PERMISSION_DENIED,
                             {'PERMISSION': {
                                 'premium_requirements': premium_requirements},
                                 'username': username})
                raise Http_error(403, Message.ACCESS_DENIED)
    return {'access_type': access_type}


