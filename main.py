from uuid import uuid4

from bottle import Bottle, run, hook, request

import logging
import sentry
from helper import Http_error
from log import logger, LogMsg
from messages import Message




from register.urls import call_router as register_routes
from user.urls import call_router as user_routes
from sign_up.urls import call_router as signup_routes
from app_token.urls import call_router as token_routes
from books.urls import call_router as book_routes
from file_handler.urls import call_router as file_routes
from comment.urls import call_router as comment_routes
from follow.urls import call_router as follow_routes
from book_rate.urls import call_router as rate_routes
from wish_list.urls import call_router as wish_routes
from book_collections.urls import call_router as collection_routes
from accounts.urls import call_router as account_routes
from financial_transactions.urls import call_router as transaction_routes
from prices.urls import call_router as price_routes
from order.urls import call_router as order_routes
from book_library.urls import  call_router as library_routes
from group.urls import call_router as group_routes
from permission.urls import call_router as permission_routes
from discussion_group.urls import call_router as discussion_routes
from messaging.urls import call_router as messaging_routes
from payment.urls import call_router as payment_routes
from db_migration.urls import call_router as db_routse
from celery_works.urls import call_router as celery_routes
from run_process.urls import call_router as process_routes
from book_encription.urls import call_router as encription_routes
from reports.urls import call_router as reports_routes


app = Bottle()

app.catchall = False
# app = Sentry(app, sentry.sentry_client)
#
user_routes(app)
register_routes(app)
signup_routes(app)
token_routes(app)
book_routes(app)
file_routes(app)
comment_routes(app)
follow_routes(app)
rate_routes(app)
wish_routes(app)
collection_routes(app)
account_routes(app)
transaction_routes(app)
price_routes(app)
order_routes(app)
library_routes(app)
group_routes(app)
permission_routes(app)
discussion_routes(app)
messaging_routes(app)
payment_routes(app)
db_routse(app)
celery_routes(app)
process_routes(app)
encription_routes(app)
reports_routes(app)

if __name__ == '__main__':
    print('hello world')


    @hook('before_request')
    def generate_RID():
        try:

            request.JJP_RID = 'JJP_{}'.format(uuid4())
            logger.debug('JJP_RID:{}'.format(request.JJP_RID))

        except:
            logger.exception(LogMsg.RID_OPERATION_FAILED, exc_info=True)
            raise Http_error(409, Message.RID_OPERATION_FAILED)


    run(host='0.0.0.0', port=7000, debug=True, app=app)


