from telegram.ext import CallbackQueryHandler

from ..language import get_text
from .messages import ask_a_boolean_question, send_a_rating_message
from ..database.manipulation import add_rating_to_an_order

from ..utils.consts import *



PATTERN_TO_CATCH_THE_RATE = "rate_product"
PATTERN_TO_CATCH_IF_USER_WANT_RATE_THE_PRODUCT = (
    "rate_product")


#------------------------------------------------------------
def store_rating_response(context, rating):
    pre_checkout_query = context.chat_data["last_order"] 
    order_id = pre_checkout_query.id
    add_rating_to_an_order(order_id, rating)

#------------------------------------------------------------
def ask_if_user_want_evaluate_the_product(update, context, product):
    ask_a_boolean_question(
        update, 
        context,
        PATTERN_TO_CATCH_IF_USER_WANT_RATE_THE_PRODUCT,
        get_text("ask_if_user_want_evaluate_the_product", context))

#------------------------------------------------------------
def catch_the_response_if_user_want_evaluate(update, context):
    query = update.callback_query
    if query.data == (PATTERN_TO_CATCH_IF_USER_WANT_RATE_THE_PRODUCT + 'OK'):
        send_a_rating_message(
            update, 
            context,
            PATTERN_TO_CATCH_THE_RATE)
    elif query.data == (
        PATTERN_TO_CATCH_IF_USER_WANT_RATE_THE_PRODUCT + 'cancel'):
        query.edit_message_text(get_text("OK", context))

#------------------------------------------------------------
def catch_the_rating_response_callback(update, context):
    query = update.callback_query
    try:
        rating = int(query.data.replace(PATTERN_TO_CATCH_THE_RATE, ""))
        store_rating_response(context, rating)
        query.edit_message_text(get_text("thanks_opinion", context))
    except: 
        query.edit_message_text(get_text("cancelled_operation", context))

#------------------------------------------------------------
#------------------------------------------------------------
catch_the_response_if_user_want_evaluate_handler = CallbackQueryHandler(
    catch_the_response_if_user_want_evaluate, 
    pattern = PATTERN_TO_CATCH_IF_USER_WANT_RATE_THE_PRODUCT)

#------------------------------------------------------------
#------------------------------------------------------------
catch_the_rating_handler = CallbackQueryHandler(
    catch_the_rating_response_callback, 
    pattern = PATTERN_TO_CATCH_THE_RATE)

#------------------------------------------------------------
#------------------------------------------------------------
rating_precess_handlers = [catch_the_rating_handler,
    catch_the_response_if_user_want_evaluate_handler]


