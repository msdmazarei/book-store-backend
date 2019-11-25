from .controllers import device_key
from helper import check_auth, inject_db, jsonify, pass_data


def call_router(app):
    readonly_wrappers = [inject_db, jsonify]
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/device-keys/<id>', 'GET', device_key.get, apply=wrappers)
    app.route('/device-keys/_search', 'POST', device_key.get_all,
              apply=data_plus_wrappers)
    app.route('/device-keys/<id>', 'DELETE', device_key.delete,
              apply=[check_auth, inject_db])


    app.route('/device-keys', 'POST', device_key.add,apply=data_plus_wrappers)
    app.route('/device-keys/user/<user_id>', 'GEt', device_key.get_user_devices,
          apply=wrappers)
