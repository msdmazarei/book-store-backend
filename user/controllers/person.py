import json
import os
from sqlalchemy import or_
from accounts.controller import add_initial_account
from book_library.controller import is_book_in_library
from check_permission import get_user_permissions, has_permission_or_not, \
    has_permission
from enums import Permissions
from follow.controller import get_following_list_internal
from helper import model_to_dict, Http_error, model_basic_dict, \
    populate_basic_data, edit_basic_data, Http_response
from log import LogMsg, logger
from messages import Message
from repository.account_repo import delete_person_accounts
from repository.book_role_repo import person_has_books
from repository.user_repo import check_user
from wish_list.controller import internal_wish_list
from ..models import Person, User
from repository.person_repo import person_cell_exists, person_mail_exists
from books.controllers.book import get_current_book
from configs import SIGNUP_USER, ADMINISTRATORS
from constraint_handler.controllers.person_constraint import \
    add as add_uniquecode, persons_code
from constraint_handler.controllers.unique_entity_connector import \
    get_by_entity as get_connector, add as add_connector, \
    delete as delete_connector
from constraint_handler.controllers.common_methods import \
    delete as delete_uniquecode
from infrastructure.schema_validator import schema_validate
from ..constants import PERSON_ADD_SCHEMA_PATH,PERSON_EDIT_SCHEMA_PATH

save_path = os.environ.get('save_path')


def add(db_session, data, username):
    logger.info(LogMsg.START, username)
    schema_validate(data,PERSON_ADD_SCHEMA_PATH)

    if username is not None and username != SIGNUP_USER:
        permissions, presses = get_user_permissions(username, db_session)
        has_permission([Permissions.PERSON_ADD_PREMIUM],
                       permissions)
        logger.debug(LogMsg.PERMISSION_VERIFIED)

    cell_no = data.get('cell_no')
    if cell_no and person_cell_exists(db_session, cell_no):
        logger.error(LogMsg.PERSON_EXISTS, {'cell_no': cell_no})
        raise Http_error(409, Message.ALREADY_EXISTS)

    email = data.get('email')

    if email and person_mail_exists(db_session, email):
        logger.error(LogMsg.PERSON_EXISTS, {'email': email})
        raise Http_error(409, Message.ALREADY_EXISTS)

    logger.debug(LogMsg.CHECK_UNIQUE_EXISTANCE, data)

    model_instance = Person()
    populate_basic_data(model_instance, username, data.get('tags'))
    logger.debug(LogMsg.POPULATING_BASIC_DATA)
    model_instance.name = data.get('name')
    model_instance.last_name = data.get('last_name')
    model_instance.full_name = full_name(model_instance.name,model_instance.last_name)
    model_instance.address = data.get('address')
    model_instance.phone = data.get('phone')
    model_instance.email = data.get('email')
    model_instance.cell_no = data.get('cell_no')
    model_instance.bio = data.get('bio')
    model_instance.image = data.get('image')
    model_instance.is_legal = data.get('is_legal', False)

    unique_code = add_uniquecode(model_instance, db_session)
    db_session.add(model_instance)

    db_session.flush()
    logger.debug(LogMsg.DB_ADD)
    add_initial_account(model_instance.id, db_session, username)
    logger.debug(LogMsg.PERSON_ADD_ACCOUNT, {'person_id': model_instance.id})

    add_connector(model_instance.id, unique_code.UniqueCode, db_session)
    logger.debug(LogMsg.UNIQUE_CONNECTOR_ADDED, {'person_id': model_instance.id,
                                                 'unique_constraint': unique_code.UniqueCode})
    logger.info(LogMsg.END)
    return model_instance


def get(id, db_session, username=None):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(Person).filter(Person.id == id).first()
    if model_instance:
        person_dict = person_to_dict(model_instance, db_session)
        logger.debug(LogMsg.GET_SUCCESS +
                     json.dumps(person_dict))
    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.NOT_FOUND)

    if username is not None:
        user = check_user(username, db_session)
        per_data = {}
        permissions, presses = get_user_permissions(username, db_session)
        if user.person_id == id:
            per_data.update({Permissions.IS_OWNER.value: True})
        has_permission([Permissions.PERSON_GET_PREMIUM],
                       permissions, None, per_data)
        logger.debug(LogMsg.PERMISSION_VERIFIED)
    logger.info(LogMsg.END)

    return person_dict


def edit(id, db_session, data, username):
    logger.info(LogMsg.START, username)

    schema_validate(data,PERSON_EDIT_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)

    logger.debug(LogMsg.EDIT_REQUST, {'person_id': id, 'data': data})


    user = check_user(username, db_session)
    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON, username)
        raise Http_error(404, Message.INVALID_USER)

    model_instance = db_session.query(Person).filter(Person.id == id).first()
    if model_instance:
        logger.debug(LogMsg.MODEL_GETTING)
    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED, {'person_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    per_data = {}
    permissions, presses = get_user_permissions(username, db_session)
    if user.person_id == id:
        per_data.update({Permissions.IS_OWNER.value: True})
    has_permission([Permissions.PERSON_EDIT_PREMIUM],
                   permissions, None, per_data)
    logger.debug(LogMsg.PERMISSION_VERIFIED)

    if 'current_book_id' in data.keys():
        if not is_book_in_library(model_instance.id, data.get('current_book_id'),
                                  db_session):
            logger.error(LogMsg.COLLECTION_BOOK_IS_NOT_IN_LIBRARY,
                         {'current_book_id': data.get('current_book_id')})
            raise Http_error(404, Message.BOOK_NOT_IN_LIB)
    if 'cell_no' in data.keys():
        cell_person = person_cell_exists(db_session, data.get('cell_no'))
        if cell_person is not None:
            if cell_person.id != model_instance.id:
                logger.error(LogMsg.ANOTHER_PERSON_BY_CELL)
                raise Http_error(403, Message.CELL_EXISTS)

    try:
        for key, value in data.items():
            # TODO  if key is valid attribute of class
            setattr(model_instance, key, value)
        model_instance.full_name = full_name(model_instance.name,model_instance.last_name)

        edit_basic_data(model_instance, username, data.get('tags'))
        db_session.flush()

        logger.debug(LogMsg.MODEL_ALTERED,
                     person_to_dict(model_instance, db_session))

        logger.debug(LogMsg.UNIQUE_CONSTRAINT_IS_CHANGING)
        unique_connector = get_connector(id, db_session)
        if unique_connector:
            if persons_code(model_instance) != unique_connector.UniqueCode:
                logger.debug(LogMsg.DELETE_UNIQUE_CONSTRAINT)
                delete_uniquecode(unique_connector.UniqueCode, db_session)
                db_session.flush()
                logger.debug(LogMsg.GENERATE_UNIQUE_CONSTRAINT, data)
                code = add_uniquecode(model_instance, db_session)
                delete_connector(id, db_session)
                add_connector(id, code.UniqueCode, db_session)
    except:
        logger.exception(LogMsg.EDIT_FAILED, exc_info=True)
        raise Http_error(500, Message.DELETE_FAILED)

    logger.info(LogMsg.END)
    return model_instance


def delete(id, db_session, username):
    logger.info(LogMsg.START, username)

    logger.info(LogMsg.DELETE_REQUEST, {'person_id': id})

    model_instance = db_session.query(Person).filter(Person.id == id).first()
    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'person_id': id})
        raise Http_error(404, Message.NOT_FOUND)
    user = check_user(username, db_session)
    per_data = {}
    permissions, presses = get_user_permissions(username, db_session)
    if user.person_id == id:
        per_data.update({Permissions.IS_OWNER.value: True})
    has_permission([Permissions.PERSON_DELETE_PREMIUM],
                   permissions, None, per_data)
    logger.debug(LogMsg.PERMISSION_VERIFIED)
    if person_has_books(id, db_session):
        logger.error(LogMsg.PERSON_HAS_BOOKS, {'person_id': id})
        raise Http_error(403, Message.PERSON_HAS_BOOKS)

    try:
        delete_person_accounts(id, db_session)
        logger.debug(LogMsg.PERSON_ACCOUNTS_DELETED, {'person_id': id})
        db_session.delete(model_instance)
        logger.debug(LogMsg.PERSON_DELETED, {'person_id': id})

        users = db_session.query(User).filter(User.person_id == id).all()
        logger.debug(LogMsg.PERSON_USERS_GOT, id)
        if users is not None:
            for user in users:
                logger.debug(LogMsg.RELATED_USER_DELETE,
                             {'person_id': id, 'user_id': user.id})

                db_session.delete(user)
                logger.debug(LogMsg.ENTITY_DELETED)
        else:
            logger.debug(LogMsg.NOT_RELATED_USER_FOR_PERSON,
                         {"Person.id {}": id})

        unique_connector = get_connector(id, db_session)
        if unique_connector:
            logger.debug(LogMsg.DELETE_UNIQUE_CONSTRAINT)
            delete_uniquecode(unique_connector.UniqueCode, db_session)
            delete_connector(id, db_session)

    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(500, Message.DELETE_FAILED)

    logger.info(LogMsg.END)

    return Http_response(204, True)


def get_all(db_session, username):
    logger.info(LogMsg.START, username)

    permissions, presses = get_user_permissions(username, db_session)
    has_permission([Permissions.PERSON_GET_PREMIUM], permissions)
    logger.debug(LogMsg.PERMISSION_VERIFIED)
    try:
        result = db_session.query(Person).all()
        logger.debug(LogMsg.GET_SUCCESS)
    except:
        logger.error(LogMsg.GET_FAILED)
        raise Http_error(500, LogMsg.GET_FAILED)

    logger.debug(LogMsg.END)
    return result


def search_person(data, db_session, username):
    if data.get('sort') is None:
        data['sort'] = ['creation_date-']

    result = []

    permissions, presses = get_user_permissions(username, db_session)
    has_permission([Permissions.PERSON_GET_PREMIUM], permissions)
    logger.debug(LogMsg.PERMISSION_VERIFIED)


    try:
        persons = Person.mongoquery(
            db_session.query(Person)).query(
            **data).end().all()

        for person in persons:
            result.append(model_to_dict(person))
        logger.debug(LogMsg.GET_SUCCESS, result)
    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        raise Http_error(404, Message.NOT_FOUND)
    logger.info(LogMsg.END)
    return result


def get_person_profile(id, db_session, username):
    logger.info(LogMsg.START, username)
    user = check_user(username, db_session)
    per_data = {}
    permissions, presses = get_user_permissions(username, db_session)
    if user.person_id == id:
        per_data.update({Permissions.IS_OWNER.value: True})
    has_permission([Permissions.PERSON_GET_PREMIUM],
                   permissions, None, per_data)
    logger.debug(LogMsg.PERMISSION_VERIFIED)
    logger.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(Person).filter(Person.id == id).first()
    if model_instance:
        result = model_to_dict(model_instance)
        result['current_book'] = get_current_book(
            model_instance.current_book_id, db_session) or None
        result['following_list'] = list(get_following_list_internal(id, db_session))
        result['wish_list'] = list(internal_wish_list(db_session, id))

        logger.debug(LogMsg.GET_SUCCESS, result)
    else:
        logger.error(LogMsg.NOT_FOUND, {"Person_id": id})
        raise Http_error(404, Message.NOT_FOUND)
    logger.info(LogMsg.END)

    return result


def person_to_dict(person, db_session=None):
    result = model_basic_dict(person)
    model_attrs = {
        'address': person.address,
        'bio': person.bio,
        'cell_no': person.cell_no,
        'current_book_id': person.current_book_id,
        'email': person.email,
        'image': person.image,
        'name': person.name,
        'last_name': person.last_name,
        'full_name': person.full_name,
        'phone': person.phone
        # 'library':library_to_dict(person.library,db_session)

    }
    if person.is_legal is None:
        result['is_legal'] = False
    else:
        result['is_legal'] = person.is_legal
    result.update(model_attrs)
    return result


def full_name(name,last_name):
    if name is None or (name==''):
        full_name = last_name
    elif last_name is None or(last_name==''):
        full_name = name
    else:
        full_name = '{} {}'.format(name,last_name)
    return full_name