from group.models import Group
from helper import Http_error
from log import logger, LogMsg
from messages import Message


def validate_groups(group_list, db_session):
    result = db_session.query(Group).filter(
        Group.id.in_(set(group_list))).all()
    if (result is not None) and (len(set(group_list)) == len(result)):
        return result
    else:
        raise Http_error(404, Message.INVALID_GROUP)


def validate_group(group_id, db_session):
    group = db_session.query(Group).filter(
        Group.id == group_id).first()
    if group is None:
        logger.error(LogMsg.GROUP_INVALID, {'group_id': group_id})
        raise Http_error(404, Message.INVALID_GROUP)
    return group


def check_group_title_exists(title, db_session):
    result = db_session.query(Group).filter(Group.title == title).first()
    if result is None:
        return False
    return True


def groups_by_presses(press_list, db_session):
    result = db_session.query(Group).filter(
        Group.person_id.in_(press_list)).all()
    final_res = []
    for group in result:
        final_res.append(group.id)
    return final_res


def limit_groups_by_person(group_ids, person_id, db_session):
    result = db_session.query(Group).filter(Group.id.in_(group_ids),
                                            Group.person_id == person_id).all()
    final_res = []
    for item in result:
        final_res.append(item.id)
    return final_res


def groups_by_press(press, db_session):
    result = db_session.query(Group).filter(
        Group.person_id==press).all()
    final_res = []
    for group in result:
        final_res.append(group.id)
    return final_res