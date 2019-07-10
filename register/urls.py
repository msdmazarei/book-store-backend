from .controller import register, app_ping, activate_account,forget_pass
from helper import check_auth, inject_db, jsonify, pass_data


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/register/activate-acount', 'POST', activate_account,
              apply=[inject_db, pass_data,jsonify])

    app.route('/register/send-code', 'POST', register,
              apply=[inject_db, pass_data, jsonify])

    app.route('/forget-password/send-code', 'POST', forget_pass,
              apply=[inject_db, pass_data, jsonify])

    app.route('/ping', 'GET', app_ping)