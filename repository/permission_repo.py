from permission.models import Permission


def get_permissions_values(permission_list, db_session):
    result = db_session.query(Permission).filter(
        Permission.id.in_(set(permission_list))).all()
    permission_values = []
    for item in result:
        permission_values.append(item.permission)
    return permission_values

