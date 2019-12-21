from helper import check_auth, inject_db, jsonify, pass_data,timeit
from payment.controllers.kipo_pay import receive_payment, pay_by_kipo, sample_html_form
from payment.controllers.payment import get_all

def call_router(app):
    wrappers = [check_auth, inject_db, jsonify,timeit]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/payment-receive', 'GET', receive_payment,
              apply=[inject_db,timeit])
    app.route('/payment-send', 'POST', pay_by_kipo, apply=[inject_db,pass_data,check_auth,timeit])
    app.route('/payment-sample','GET',sample_html_form,apply=[inject_db,pass_data,timeit])

    app.route('/payment/_search', 'POST', get_all, apply=data_plus_wrappers)

