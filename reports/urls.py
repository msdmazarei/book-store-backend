from helper import check_auth, inject_db, jsonify, pass_data
from .controllers import report

def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/reports/book-of-month', 'GET', report.book_of_month, apply=wrappers)
