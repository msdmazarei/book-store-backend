from helper import check_auth, inject_db, jsonify, pass_data
from .controller import get_personal_library,delete,edit_status,get_user_library,head_user_library


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/library/user', 'POST', get_personal_library, apply=data_plus_wrappers)
    app.route('/library/<id>', 'DELETE', delete,apply=[check_auth, inject_db])
    app.route('/library/<id>', 'PUT', edit_status,apply=data_plus_wrappers)
    app.route('/library/user/<person_id>', 'GET', get_user_library, apply=wrappers)
    app.route('/library/user', 'HEAD', head_user_library, apply=[check_auth,inject_db])

