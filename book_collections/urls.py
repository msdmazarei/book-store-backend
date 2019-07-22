from helper import check_auth, inject_db, jsonify, pass_data
from .controller import add, get_all_collections, get_collection, \
    delete_collection, delete_books_from_collection


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/collections/remove-books', 'DELETE',
              delete_books_from_collection,
              apply=[check_auth, inject_db, pass_data])
    app.route('/collections/<title>', 'DELETE', delete_collection,
              apply=[check_auth, inject_db])
    app.route('/collections', 'POST', add, apply=data_plus_wrappers)
    app.route('/collections', 'GET', get_all_collections, apply=wrappers)
    app.route('/collections/<title>', 'GET', get_collection, apply=wrappers)