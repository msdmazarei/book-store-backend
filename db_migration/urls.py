from helper import check_auth, inject_db, jsonify, pass_data,timeit
from .book import book_press_settling
from .permissions import permissions_to_db
from .person import full_name_settling,full_name_erasing


def call_router(app):
    readonly_wrappers = [inject_db, jsonify,timeit]
    wrappers = [check_auth, inject_db, jsonify,timeit]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/book-press-settle', 'GET', book_press_settling, apply=wrappers)
    app.route('/permissions/inject-db', 'POST',permissions_to_db , apply=wrappers)
    app.route('/full-name-settle', 'GET', full_name_settling, apply=wrappers)
    app.route('/full-name-erase', 'GET', full_name_erasing, apply=wrappers)


