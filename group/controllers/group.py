import os

from check_permission import get_user_permissions, has_permission, \
    has_permission_or_not, validate_permissions_and_access
from configs import ADMINISTRATORS
from enums import Permissions, Access_level
from helper import model_to_dict, Http_error, model_basic_dict, \
    populate_basic_data, edit_basic_data, Http_response
from log import LogMsg, logger
from messages import Message
from repository.group_permission import \
    delete_all_permissions_of_group
from repository.group_repo import check_group_title_exists
from repository.group_user_repo import delete_group_users, user_is_in_group, \
    add_owner_to_group_users
from repository.user_repo import check_user
from user.controllers.user import get_by_person
from ..constants import GROUP_EDIT_SCHEMA_PATH, GROUP_ADD_SCHEMA_PATH
from infrastructure.schema_validator import schema_validate
from user.controllers.person import get as get_person
from repository.person_repo import validate_person
from ..models import Group

save_path = os.environ.get('save_path')


def add(data, db_session, username):
    logger.info(LogMsg.START, username)

    schema_validate(data, GROUP_ADD_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)

    person_id = data.get('person_id', None)
    if person_id is not None:
        owner_person = validate_person(person_id, db_session)
        if owner_person is not None and not owner_person.is_legal:
            logger.error(LogMsg.PERSON_IS_NOT_LEGAL, username)
            raise Http_error(400, Message.PERSON_IS_NOT_LEGAL)
        owner_user = get_by_person(person_id, db_session)
        if owner_user is None:
            logger.error(LogMsg.PERSON_MUST_HAVE_USER, person_id)
            raise Http_error(404, Message.PERSON_MUST_HAVE_USER)

    user = check_user(username, db_session)

    if username not in ADMINISTRATORS:

        permissions, presses = get_user_permissions(username, db_session)
        permit = has_permission_or_not(
            [Permissions.PERMISSION_GROUP_ADD_PREMIUM],
            permissions)
        if not permit:
            press_permit = has_permission_or_not(
                [Permissions.PERMISSION_GROUP_ADD_PRESS],
                permissions)
            if not (press_permit and (person_id == user.person_id)):
                logger.error(LogMsg.PERMISSION_DENIED,
                             {'PERMISSION_GROUP_ADD': username})
                raise Http_error(403, Message.ACCESS_DENIED)

        if check_group_title_exists(data.get('title', None), db_session):
            logger.error(LogMsg.GROUP_EXISTS)
            raise Http_error(409, Message.ALREADY_EXISTS)

    model_instance = Group()
    populate_basic_data(model_instance, username, data.get('tags'))
    logger.debug(LogMsg.POPULATING_BASIC_DATA)
    model_instance.title = data.get('title')
    model_instance.person_id = data.get('person_id')
    db_session.add(model_instance)
    # db_session.flush()
    add_owner_to_group_users(model_instance.id, owner_user.id, db_session,
                             username)

    logger.info(LogMsg.END)
    return model_instance


def get(id, db_session, username=None):
    logger.info(LogMsg.START, username)
    if username is not None:
        user = check_user(username, db_session)
        per_data = dict()
        logger.debug(LogMsg.PERMISSION_CHECK, username)
        if user_is_in_group(user.id, id, db_session):
            per_data = {Permissions.IS_MEMBER.value: True}
        validate_permissions_and_access(username, db_session,
                                        'PERMISSION_GROUP_GET', per_data)
        logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    logger.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(Group).filter(Group.id == id).first()
    if model_instance:
        logger.debug(LogMsg.GET_SUCCESS,
                     model_to_dict(model_instance))
    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.NOT_FOUND)
    logger.error(LogMsg.GET_FAILED, {"id": id})
    logger.info(LogMsg.END)

    return model_instance


def edit(id, db_session, data, username):
    logger.info(LogMsg.START, username)
    user = check_user(username, db_session)

    logger.debug(LogMsg.EDIT_REQUST, {'group_id': id, 'data': data})
    schema_validate(data, GROUP_EDIT_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)

    model_instance = db_session.query(Group).filter(Group.id == id).first()
    if model_instance:
        logger.debug(LogMsg.MODEL_GETTING)
    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED, {'group_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session,
                                    'PERMISSION_GROUP_EDIT',
                                    model=model_instance)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    person_id = data.get('person_id', None)
    if person_id is not None:
        owner_person = get_person(person_id, db_session)
        if owner_person is not None and not owner_person.is_legal:
            logger.error(LogMsg.PERSON_IS_NOT_LEGAL, username)
            raise Http_error(400, Message.PERSON_IS_NOT_LEGAL)
        owner_user = get_by_person(person_id, db_session)
        if owner_user is None:
            logger.error(LogMsg.PERSON_MUST_HAVE_USER, person_id)
            raise Http_error(404, Message.PERSON_MUST_HAVE_USER)

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

    logger.info(LogMsg.DELETE_REQUEST, {'group_id': id})
    user = check_user(username, db_session)

    model_instance = db_session.query(Group).filter(Group.id == id).first()
    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'group_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session,
                                    'PERMISSION_GROUP_DELETE',
                                    model=model_instance)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    try:
        logger.debug(LogMsg.DELETE_GROUP_USERS, {'group_id': id})
        delete_group_users(model_instance.id, db_session)
        logger.debug(LogMsg.GROUP_DELETE_PERMISSIONS, {'group_id': id})
        delete_all_permissions_of_group(model_instance.id, db_session)
        logger.debug(LogMsg.GROUP_DELETE, id)

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
                                    'PERMISSION_GROUP_GET',
                                    access_level=Access_level.Premium)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    if data.get('sort') is None:
        data['sort'] = ['creation_date-']

    try:
        result = Group.mongoquery(db_session.query(Group)).query(
            **data).end().all()
        logger.debug(LogMsg.GET_SUCCESS)
    except:
        logger.error(LogMsg.GET_FAILED)
        raise Http_error(500, LogMsg.GET_FAILED)

    logger.debug(LogMsg.END)
    return result


def search_group(data, db_session, username=None):
    if username is not None:
        user = check_user(username, db_session)

        logger.debug(LogMsg.PERMISSION_CHECK, username)
        validate_permissions_and_access(username, db_session,
                                        'PERMISSION_GROUP_GET')
        logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    if data.get('sort') is None:
        data['sort'] = ['creation_date-']

    result = []
    groups = Group.mongoquery(db_session.query(Group)).query(**data).end().all()
    for group in groups:
        result.append(model_to_dict(group))

        if username is not None and not (
                user_is_in_group(user.id, group.id, db_session)):
            del result[-1]

    logger.debug(LogMsg.GET_SUCCESS, result)

    logger.info(LogMsg.END)
    return result
