from check_permission import validate_permissions_and_access
from enums import Access_level
from helper import populate_basic_data, model_to_dict, model_basic_dict, Http_error, \
    edit_basic_data, Http_response
from infrastructure.schema_validator import schema_validate
from log import logger, LogMsg
from messages import Message
from payment.models import CheckoutPressAccount
from repository.user_repo import check_user
from user.controllers.person import person_to_dict
from ..constants import CHECKOUT_ADD_SCHEMA_PATH, CHECKOUT_EDIT_SCHEMA_PATH


def add_payment(data, db_session, username):
    logger.info(LogMsg.START, username)
    schema_validate(data, CHECKOUT_ADD_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)

    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session,
                                    'CHECKOUT_PAYMENT_ADD',
                                    access_level=Access_level.Premium)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    model_instance = CheckoutPressAccount()
    populate_basic_data(model_instance, username)
    logger.debug(LogMsg.POPULATING_BASIC_DATA)

    model_instance.amount = data.get('amount')
    model_instance.payer_id = data.get('payer_id')
    model_instance.receiver_id = data.get('receiver_id')
    model_instance.receiver_account_id = data.get('receiver_account_id')
    model_instance.payment_details = data.get('payment_details')

    db_session.add(model_instance)

    logger.debug(LogMsg.DB_ADD, model_to_dict(model_instance))
    logger.info(LogMsg.END)
    return model_instance


def get(id, db_session, username):
    logger.info(LogMsg.START, username)
    model_instance = db_session.query(CheckoutPressAccount).filter(
        CheckoutPressAccount.id == id).first()

    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session,
                                    'CHECKOUT_PAYMENT_GET', model=model_instance,
                                    access_level=Access_level.Premium)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)
    logger.info(LogMsg.END)
    return pay_model_to_dict(model_instance)


def internal_get(id, db_session):
    return db_session.query(CheckoutPressAccount).filter(
        CheckoutPressAccount.id == id).first()


def edit(id, data, db_session, username):
    logger.info(LogMsg.START, username)
    schema_validate(data, CHECKOUT_ADD_SCHEMA_PATH)
    logger.debug(LogMsg.SCHEMA_CHECKED)

    model_instance = internal_get(id, db_session)
    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'checkout_press_payment_id': id})
        raise Http_error(404, Message.NOT_FOUND)
    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session,
                                    'CHECKOUT_PAYMENT_EDIT',
                                    access_level=Access_level.Premium)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)
    try:
        edit_basic_data(model_instance, username, data.get('tags'))
        for key, value in data.items():
            setattr(model_instance, key, value)
        logger.debug(LogMsg.MODEL_ALTERED, {'CHECKOUT_PRESS_PAYMENT_ID': id})
    except:
        logger.exception(LogMsg.EDIT_FAILED, exc_info=True)
        raise Http_error(500, Message.EDIT_FAILED)
    logger.info(LogMsg.END)
    return pay_model_to_dict(model_instance)


def delete(id, db_session, username):
    logger.info(LogMsg.START, username)

    model_instance = internal_get(id, db_session)
    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'checkout_press_payment_id': id})
        raise Http_error(404, Message.NOT_FOUND)
    logger.debug(LogMsg.PERMISSION_CHECK, username)
    validate_permissions_and_access(username, db_session,
                                    'CHECKOUT_PAYMENT_DELETE',
                                    access_level=Access_level.Premium)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)
    try:
        db_session.delete(model_instance)
        logger.debug(LogMsg.DELETE_SUCCESS, {'CHECKOUT_PRESS_PAYMENT_ID': id})
    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(500, Message.DELETE_FAILED)
    logger.info(LogMsg.END)
    return Http_response(204, True)


def get_all(db_session, data, username):
    logger.info(LogMsg.START, username)
    user = check_user(username, db_session)
    logger.debug(LogMsg.PERMISSION_CHECK, username)
    access_type = validate_permissions_and_access(username, db_session,
                                                  'CHECKOUT_PAYMENT_GET')
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)
    if data.get('sort') is None:
        data['sort'] = ['creation_date-']
    try:
        final_res = []
        mq = CheckoutPressAccount.mongoquery(
            db_session.query(CheckoutPressAccount))
        # data=dict(filter=dict(title="hello"))
        result = mq.query(**data).end().all()

        logger.debug(LogMsg.GET_SUCCESS)

        for item in result:
            if access_type == 'Press':
                if item.receiver_id == user.person_id:
                    final_res.append(pay_model_to_dict(item))
            else:
                final_res.append(pay_model_to_dict(item))
    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        raise Http_error(500, Message.GET_FAILED)

    logger.debug(LogMsg.END)
    return final_res


def get_all_paid_for_person(person_id, db_session, username):
    logger.info(LogMsg.START, username)
    result = db_session.query(CheckoutPressAccount).filter(
        CheckoutPressAccount.receiver_id == person_id).all()
    count = len(result)
    total_paid = 0.0
    final_res = []
    for item in result:
        total_paid+=item.amount
        final_res.append(pay_model_to_dict(item))
    logger.info(LogMsg.END)
    return {'total_paid':total_paid,'count':count,'payment_details':final_res}



def pay_model_to_dict(model):
    result = model_basic_dict(model)
    result.update({
        'amount': model.amount,
        'payer_id': model.payer_id,
        'receiver_id': model.receiver_id,
        'receiver_account_id': model.receiver_account_id,
        'payment_details': model.payment_details,
        'receiver': person_to_dict(model.receiver)
    })
    return result
