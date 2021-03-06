from check_permission import get_user_permissions, has_permission, \
    has_permission_or_not
from enums import Permissions
from .models import Price
from helper import Http_error, populate_basic_data, Http_response, \
    model_to_dict, check_schema
from log import LogMsg, logger
from messages import Message
from repository.book_repo import get as get_book
from configs import ADMINISTRATORS, ONLINE_BOOK_TYPES
from infrastructure.schema_validator import schema_validate
from .constants import ADD_SCHEMA_PATH,EDIT_SCHEMA_PATH


def add(data, db_session, username):
    logger.info(LogMsg.START, username)

    schema_validate(data,ADD_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)

    book_id = data.get('book_id')
    book = get_book(book_id, db_session)

    if username is not None:
        per_data = {}
        permissions, presses = get_user_permissions(username, db_session)

        if book.creator == username:
            per_data.update({Permissions.IS_OWNER.value:True})
        has_permit = has_permission_or_not([Permissions.PRICE_ADD_PREMIUM], permissions,None,per_data)
        if not has_permit:
            if book.press in presses:
                has_permission([Permissions.PRICE_ADD_PRESS], permissions)
            else:
                logger.error(LogMsg.PERMISSION_DENIED,username)
                raise Http_error(403,Message.ACCESS_DENIED)
        logger.debug(LogMsg.PERMISSION_VERIFIED)

    logger.debug(LogMsg.CHECK_BOOK_PRICE_EXISTANCE, book_id)

    model_instance = get_by_book(book_id, db_session, username)
    if model_instance:
        logger.debug(LogMsg.BOOK_PRICE_EXISTS, book_id)
        logger.debug(LogMsg.EDIT_PRICE, book_id)
        model_instance.price = data.get('price')

    else:
        logger.debug(LogMsg.ADD_NEW_BOOK_PRICE, book_id)
        model_instance = Price()

        populate_basic_data(model_instance, username)
        model_instance.book_id = book_id
        model_instance.price = data.get('price')

        db_session.add(model_instance)
    logger.info(LogMsg.END)

    return model_instance


def get_by_book(book_id, db_session, username=None):
    logger.info(LogMsg.START, username)

    return db_session.query(Price).filter(Price.book_id == book_id).first()


def get_all(data, db_session, username=None):
    logger.info(LogMsg.START, username)

    if data.get('sort') is None:
        data['sort'] = ['creation_date-']

    if username is not None:
        permissions, presses = get_user_permissions(username, db_session)
        has_permission([Permissions.PRICE_GET_PREMIUM], permissions)
        logger.debug(LogMsg.PERMISSION_VERIFIED)

    result = Price.mongoquery(
            db_session.query(Price)).query(
            **data).end().all()
    res = []
    for item in result:
        res.append(model_to_dict(item))
    logger.debug(LogMsg.GET_SUCCESS, res)
    logger.info(LogMsg.END)

    return res


def get_by_id(id, db_session, username=None):
    logger.info(LogMsg.START, username)

    return db_session.query(Price).filter(Price.id == id).first()


def delete(id, db_session, username=None):
    logger.info(LogMsg.START, username)

    price = get_by_id(id, db_session)
    if price is None:
        logger.error(LogMsg.NOT_FOUND, {'book_price_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    book = get_book(price.book_id, db_session)

    if username is not None:
        per_data = {}
        permissions, presses = get_user_permissions(username, db_session)
        if book.creator == username:
            per_data.update({Permissions.IS_OWNER.value: True})
        has_permit = has_permission_or_not([Permissions.PRICE_DELETE_PREMIUM],
                                           permissions, None, per_data)
        if not has_permit:
            if book.press in presses:
                has_permission([Permissions.PRICE_DELETE_PRESS], permissions)
            else:
                logger.error(LogMsg.PERMISSION_DENIED, username)
                raise Http_error(403, Message.ACCESS_DENIED)
        logger.debug(LogMsg.PERMISSION_VERIFIED)


    try:
        db_session.delete(price)
        logger.debug(LogMsg.DELETE_SUCCESS, {'book_price_id': id})
    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(404, Message.DELETE_FAILED)

    logger.info(LogMsg.END)

    return Http_response(204, True)


def edit(id, data, db_session, username=None):
    logger.info(LogMsg.START, username)

    schema_validate(data,EDIT_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)

    model_instance = get_by_id(id, db_session)

    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'book_price_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    book = get_book(model_instance.book_id, db_session)

    if username is not None:
        per_data = {}
        permissions, presses = get_user_permissions(username, db_session)
        if book.creator == username:
            per_data.update({Permissions.IS_OWNER.value: True})
        has_permit = has_permission_or_not([Permissions.PRICE_EDIT_PREMIUM],
                                           permissions, None, per_data)
        if not has_permit:
            if book.press in presses:
                has_permission([Permissions.PRICE_EDIT_PRESS], permissions)
            else:
                logger.error(LogMsg.PERMISSION_DENIED, username)
                raise Http_error(403, Message.ACCESS_DENIED)
        logger.debug(LogMsg.PERMISSION_VERIFIED)

    try:
        model_instance.price = data.get('price')
        logger.debug(LogMsg.EDIT_SUCCESS, model_to_dict(model_instance))
    except:
        logger.exception(LogMsg.EDIT_FAILED, exc_info=True)
        raise Http_error(404, Message.EDIT_FAILED)
    logger.info(LogMsg.END)

    return model_instance


def internal_edit(book_id, price, db_session):
    logger.info(LogMsg.START, '')
    logger.debug('price is {}'.format(price))

    model_instance = get_by_book(book_id, db_session)

    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'book_price_id':book_id })
        model_instance = add_internal(price, book_id, db_session, 'INTERNAL')
        logger.debug(LogMsg.ADDING_PRICE,model_instance)
    else:

        model_instance.price = price
        logger.debug(LogMsg.MODEL_ALTERED, model_to_dict(model_instance))

    logger.info(LogMsg.END)

    return model_instance


def get_book_price_internal(book_id, db_session):
    logger.info(LogMsg.START, '')

    model_instance = db_session.query(Price).filter(
        Price.book_id == book_id).first()
    logger.info(LogMsg.END)

    if model_instance:
        return model_instance.price
    else:
        return None


def calc_price(data, db_session, username):
    logger.info(LogMsg.START, username)

    item_prices = []
    total_price = 0.000
    check_schema(['items'], data.keys())
    logger.debug(LogMsg.SCHEMA_CHECKED)

    items = data.get('items')
    for item in items:
        book_id = item.get('book_id')
        count = item.get('count', 0)
        discount = item.get('discount', None)
        price_object = get_book_price_internal(book_id, db_session)

        if price_object is None:
            logger.error(LogMsg.PRICE_NOT_FOUND, {'book_id': book_id})
            raise Http_error(404, Message.NO_PRICE_FOUND)

        book = get_book(book_id, db_session)
        if (book.type.name in ONLINE_BOOK_TYPES) and (count > 1):
            logger.error(LogMsg.BOOK_ONLINE_TYPE_COUNT_LIMITATION)
            raise Http_error(400, Message.ONLINE_BOOK_COUNT_LIMITATION)

        price = price_object * count
        net_price = price
        if discount:
            if isinstance(discount, float) and discount < 1:
                effect = 1.000 - discount
                net_price = price * effect
            else:
                logger.error(LogMsg.INVALID_ENTITY_TYPE, {'discount': discount})
                raise Http_error(400, Message.DISCOUNT_IS_FLOAT)

        item_info = {'book_id': book_id, 'unit_price': price_object,
                     'count': count, 'discount': discount,
                     'net_price': net_price}
        logger.debug(LogMsg.PRICE_ITEM_CALC, item_info)
        item_prices.append(item_info)
        total_price += net_price

    final_res = {'items': item_prices, 'total_price': total_price}
    logger.debug(LogMsg.PRICE_ALL_CALCED, final_res)
    logger.info(LogMsg.END)

    return final_res


def calc_net_price(unit_price, count, discount=0.0):
    logger.info(LogMsg.START, '')

    if unit_price is None:
        raise Http_error(400, Message.NO_PRICE_FOUND)
    net_price = unit_price * count
    if discount != 0.0:
        if discount < 1.00:
            net_price = net_price * (1 - discount)
        else:
            logger.exception(LogMsg.PRICE_CALC_FAILED, exc_info=True)
            raise Http_error(404, Message.DISCOUNT_IS_FLOAT)
    logger.debug(LogMsg.PRICE_NET_CALCED,
                 {'unit_price': unit_price, 'count': count,
                  'discount': discount, 'net_price': net_price})
    logger.info(LogMsg.END)
    return net_price



def add_internal(price,book_id, db_session,username):

    logger.debug(LogMsg.CHECK_BOOK_PRICE_EXISTANCE, book_id)

    model_instance = get_by_book(book_id, db_session, username)
    if model_instance:
        logger.debug(LogMsg.BOOK_PRICE_EXISTS, book_id)
        logger.debug(LogMsg.EDIT_PRICE, book_id)
        model_instance.price = price

    else:
        logger.debug(LogMsg.ADD_NEW_BOOK_PRICE, book_id)
        model_instance = Price()

        populate_basic_data(model_instance, username)
        model_instance.book_id = book_id
        model_instance.price = price

        db_session.add(model_instance)
    logger.info(LogMsg.END)

    return model_instance