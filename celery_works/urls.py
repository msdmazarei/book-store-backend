from helper import check_auth, inject_db, jsonify, pass_data
from celery_works.main_producer import generate_book, check_status


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/generate-book', 'POST', generate_book,
              apply=[check_auth, pass_data, jsonify, inject_db])
    app.route('/generate-book/<id>', 'GET', check_status, apply=[jsonify])
