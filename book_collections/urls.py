from helper import check_auth, inject_db, jsonify, pass_data,wrappers
from .controller import add, get_all_collections, get_collection, \
    delete_collection, delete_books_from_collection, add_book_to_collections, \
    rename_collection, get_all, head_all_collections


def call_router(app):
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/collections/remove-books', 'DELETE',
              delete_books_from_collection,
              apply=[check_auth, inject_db, pass_data])
    app.route('/collections/collection', 'DELETE', delete_collection,
              apply=[check_auth, inject_db,pass_data])
    app.route('/collections', 'POST', add, apply=data_plus_wrappers)
    app.route('/collections/book', 'POST', add_book_to_collections,
              apply=data_plus_wrappers)

    app.route('/collections/user', 'POST', get_all_collections, apply=data_plus_wrappers)
    app.route('/collections/user', 'HEAD', head_all_collections, apply=[check_auth, inject_db])

    app.route('/collections/collection', 'POST', get_collection, apply=wrappers)
    app.route('/collections', 'PUT', rename_collection, apply=data_plus_wrappers)
    app.route('/collections/_search', 'POST', get_all, apply=data_plus_wrappers)

