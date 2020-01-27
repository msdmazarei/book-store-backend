from helper import check_auth, inject_db, jsonify, pass_data,timeit
from payment.controllers.kipo_pay import receive_payment, pay_by_kipo, sample_html_form
from payment.controllers.payment import get_all
from payment.controllers import checkout_press_payment

def call_router(app):
    wrappers = [check_auth, inject_db, jsonify,timeit]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/payment-receive', 'GET', receive_payment,
              apply=[inject_db,timeit])
    app.route('/payment-send', 'POST', pay_by_kipo, apply=[inject_db,pass_data,check_auth,timeit])
    app.route('/payment-sample','GET',sample_html_form,apply=[inject_db,pass_data,timeit])

    app.route('/payment/_search', 'POST', get_all, apply=data_plus_wrappers)

    app.route('/payment-press-checkout', 'POST', checkout_press_payment.add_payment,
              apply=data_plus_wrappers)
    app.route('/payment-press-checkout/<id>', 'GET', checkout_press_payment.get,
              apply=wrappers)
    app.route('/payment-press-checkout/total-paid/<person_id>', 'GET', checkout_press_payment.get_all_paid_for_person,
              apply=wrappers)

    app.route('/payment-press-checkout/_search', 'POST', checkout_press_payment.get_all, apply=data_plus_wrappers)
    app.route('/payment-press-checkout/<id>', 'PUT', checkout_press_payment.edit, apply=data_plus_wrappers)
    app.route('/payment-press-checkout/<id>', 'DELETE', checkout_press_payment.delete, apply=[check_auth,inject_db,timeit])
