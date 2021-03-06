from enums import Roles, check_enums
from helper import Http_error, model_to_dict, populate_basic_data, \
    edit_basic_data, Http_response
from infrastructure.schema_validator import schema_validate
from log import LogMsg, logger
from messages import Message
from repository.person_repo import validate_persons
from ..models import BookRole
from ..constants import ROLE_ADD_SCHEMA_PATH
from constraint_handler.controllers.unique_entity_connector import \
    get_by_entity as get_connector, add as add_connector, delete as delete_connector
from constraint_handler.controllers.book_role_constraint import add as add_uniquecode
from constraint_handler.controllers.common_methods import \
    delete as delete_uniquecode


def add(db_session, data, username):
    logger.info(LogMsg.START, username)
    schema_validate(data,ROLE_ADD_SCHEMA_PATH)

    logger.debug(LogMsg.CHECK_UNIQUE_EXISTANCE,data)
    unique_code = add_uniquecode(data, db_session)

    model_instance = BookRole()

    logger.debug(LogMsg.POPULATING_BASIC_DATA)

    populate_basic_data(model_instance, username, data.get('tags'))

    model_instance.person_id = data.get('person_id')
    model_instance.book_id = data.get('book_id')
    model_instance.role = data.get('role')

    logger.debug(LogMsg.DATA_ADDITION, book_role_to_dict(model_instance))

    db_session.add(model_instance)
    logger.debug(LogMsg.DB_ADD)

    add_connector(model_instance.id, unique_code.UniqueCode, db_session)
    logger.debug(LogMsg.UNIQUE_CONNECTOR_ADDED, {'book_role_id': model_instance.id,
                                                 'unique_constraint': unique_code.UniqueCode})

    logger.info(LogMsg.END)

    return model_instance


def add_book_roles(book_id, roles_dict_list, db_session, username):
    logger.info(LogMsg.START, username)

    result = []
    role_person = []
    role_enums = []
    persons = []

    logger.debug(LogMsg.ADDING_ROLES_OF_BOOK,
                 {'book_id': book_id, 'roles': roles_dict_list})

    for item in roles_dict_list:
        person = item.get('person')
        p_role = item.get('role')
        myperson_id = person.get('id')
        persons.append(myperson_id)
        role_enums.append(p_role)
        role_person.append({p_role: myperson_id})

    logger.debug(LogMsg.ENUM_CHECK, {'BOOK_ROLES': role_enums})

    check_enums(role_enums, Roles)

    validate_persons(persons, db_session)
    logger.debug(LogMsg.PERSON_EXISTS, {'persons': persons})

    elastic_data = {'persons': list(persons)}

    for item in role_person:
        the_role = next(iter(item))
        data = {'role': the_role,
                'book_id': book_id,
                'person_id': item[the_role]}
        if data['role'] == 'Writer':
            elastic_data['Writer'] = data['person_id']
        elif data['role'] == 'Press':
            elastic_data['Press'] = data['person_id']

        book_role = add(db_session, data, username)
        logger.debug(LogMsg.ROLE_ADDED, book_role_to_dict(book_role))

        result.append(book_role)

    logger.info(LogMsg.END)

    return result, elastic_data


def get(id, db_session):
    logger.info(LogMsg.START)

    logger.debug(LogMsg.MODEL_GETTING, id)
    model_instance = db_session.query(BookRole).filter(
        BookRole.id == id).first()
    if model_instance:
        logger.debug(LogMsg.GET_SUCCESS, book_role_to_dict(model_instance))
    else:
        logger.error(LogMsg.NOT_FOUND)
        raise Http_error(404, Message.NOT_FOUND)

    logger.info(LogMsg.END)
    return book_role_to_dict(model_instance)


def edit(id,db_session, data, username):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.EDIT_REQUST, id)

    logger.debug(LogMsg.MODEL_GETTING, id)

    model_instance = db_session.query(BookRole).filter(
        BookRole.id == id).first()
    if model_instance is not None:
        logger.debug(LogMsg.GET_SUCCESS, book_role_to_dict(model_instance))
    else:
        logger.debug(LogMsg.GET_FAILED, id)
        raise Http_error(404, Message.NOT_FOUND)

    for key, value in data.items():
        setattr(model_instance, key, value)

    logger.debug(LogMsg.EDITING_BASIC_DATA, id)
    edit_basic_data(model_instance, username, data.get('tags'))

    logger.debug(LogMsg.MODEL_ALTERED, id)

    logger.debug(LogMsg.UNIQUE_CONSTRAINT_IS_CHANGING)

    unique_connector = get_connector(id, db_session)
    if unique_connector:
        logger.debug(LogMsg.DELETE_UNIQUE_CONSTRAINT)
        delete_uniquecode(unique_connector.UniqueCode, db_session)
        logger.debug(LogMsg.GENERATE_UNIQUE_CONSTRAINT, data)
        code = add_uniquecode(data, db_session)
        delete_connector(id, db_session)
        add_connector(id, code.UniqueCode, db_session)

    logger.debug(LogMsg.EDIT_SUCCESS, book_role_to_dict(model_instance))

    logger.info(LogMsg.END)

    return book_role_to_dict(model_instance)


def delete(id, db_session, username):
    logger.info(LogMsg.START, username)

    logger.info(LogMsg.DELETE_REQUEST, id)

    logger.debug(LogMsg.MODEL_GETTING, id)
    model_instance = db_session.query(BookRole).filter(
        BookRole.id == id).first()
    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, id)
        raise Http_error(404, Message.NOT_FOUND)

    try:
        db_session.delete(model_instance)
        unique_connector = get_connector(id, db_session)
        if unique_connector:
            logger.debug(LogMsg.DELETE_UNIQUE_CONSTRAINT)
            delete_uniquecode(unique_connector.UniqueCode, db_session)
            delete_connector(id, db_session)

        logger.debug(LogMsg.ENTITY_DELETED, id)

    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(500, Message.DELETE_FAILED)

    logger.info(LogMsg.END)
    return Http_response(204, True)


def get_all(db_session,data,**kwargs):
    logger.info(LogMsg.START)

    if data.get('sort') is None:
        data['sort'] = ['creation_date-']

    try:
        result = BookRole.mongoquery(
                db_session.query(BookRole)).query(
                **data).end().all()

        logger.debug(LogMsg.GET_SUCCESS)
        res = []
        for item in result:
            res.append(book_role_to_dict(item))

    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        raise Http_error(500, Message.GET_FAILED)

    logger.debug(LogMsg.END)
    return res


def get_book_roles(book_id, db_session):
    logger.info(LogMsg.START)

    try:
        result = db_session.query(BookRole).filter(
            BookRole.book_id == book_id).all()
        logger.debug(LogMsg.GET_SUCCESS)


    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        raise Http_error(500, Message.GET_FAILED)

    logger.debug(LogMsg.END)
    return result


def delete_book_roles(book_id, db_session):
    logger.info(LogMsg.START)

    logger.debug(LogMsg.DELETE_BOOK_ROLES, book_id)

    try:
        roles = db_session.query(BookRole).filter(BookRole.book_id == book_id).all()
        for role in roles:
            unique_connector = get_connector(role.id, db_session)
            if unique_connector:
                logger.debug(LogMsg.DELETE_UNIQUE_CONSTRAINT)
                delete_uniquecode(unique_connector.UniqueCode, db_session)
                delete_connector(role.id, db_session)
                db_session.delete(role)

        logger.debug(LogMsg.DELETE_SUCCESS)


    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(500, Message.DELETE_FAILED)

    logger.debug(LogMsg.END)
    return Http_response(204, True)


def append_book_roles_dict(book_id, db_session):
    result = []
    roles = get_book_roles(book_id, db_session)
    for role in roles:
        result.append(book_role_to_dict(role))

    logger.info(LogMsg.END)

    return result


def book_role_to_dict(obj):
    if not isinstance(obj, BookRole):
        raise Http_error(500, LogMsg.NOT_RIGTH_ENTITY_PASSED.format('BookRole'))

    result = {
        'creation_date': obj.creation_date,
        'creator': obj.creator,
        'id': obj.id,
        'modification_date': obj.modification_date,
        'modifier': obj.modifier,
        'person': model_to_dict(obj.person),
        'tags': obj.tags,
        'version': obj.version,

    }

    if isinstance(obj.role, str):
        result['role'] = obj.role
    else:
        result['role'] = obj.role.name

    return result


def books_by_person(person_id, db_session):
    logger.info(LogMsg.START)
    logger.debug(LogMsg.GET_PERSONS_BOOKS, person_id)
    result = db_session.query(BookRole.book_id).filter(
        BookRole.person_id == person_id).all()
    final_res = []
    for item in result:
        final_res.append(item.book_id)

    logger.debug(LogMsg.PERSON_BOOK_LIST, final_res)
    logger.info(LogMsg.END)

    return final_res


def persons_of_book(book_id, db_session):
    logger.info(LogMsg.START)
    logger.debug(LogMsg.GETTING_ROLES_OF_BOOK, book_id)

    res = db_session.query(BookRole).filter(BookRole.book_id == book_id).all()
    persons = []
    result = {}
    for item in res:
        persons.append(item.person_id)
        if item.role.name == 'Writer':
            result['Writer'] = item.person_id
        elif item.role.name == 'Press':
            result['Press'] = item.person_id
    result.update({'persons': persons})
    logger.debug(LogMsg.BOOKS_ROLES, {'book_id': book_id, 'roles': result})

    logger.info(LogMsg.END)
    return result
