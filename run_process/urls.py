from .call_process import execute_process
from helper import check_auth, inject_db, jsonify, pass_data,timeit


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify,timeit]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/call-process', 'POST', execute_process,
              apply=data_plus_wrappers)
