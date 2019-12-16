from helper import check_auth, inject_db, jsonify, pass_data
from .controllers import report


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/reports/book-of-month-bestseller', 'GET', report.bestseller_book_of_month,
              apply=wrappers)
    app.route('/reports/book-of-week-bestseller', 'GET', report.bestseller_book_of_week,
              apply=wrappers)
    app.route('/reports/book-of-month-lowseller', 'GET', report.lowseller_book_of_month,
              apply=wrappers)
    app.route('/reports/book-of-week-lowseller', 'GET', report.lowseller_book_of_week,
              apply=wrappers)
    app.route('/reports/total-income-by-month', 'GET', report.total_annual_sale_by_month,
              apply=wrappers)
    app.route('/reports/book-by-type', 'POST', report.book_by_type,
              apply=data_plus_wrappers)
