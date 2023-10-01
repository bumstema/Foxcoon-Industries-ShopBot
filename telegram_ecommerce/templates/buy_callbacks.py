import json
import validators
#from url_metadata import metadata

from telegram import LabeledPrice,  ShippingOption, Update

from telegram.ext import (
    Filters,  ContextTypes,     CommandHandler,
    PreCheckoutQueryHandler,  ShippingQueryHandler,
    MessageHandler)

from ..language import get_text
from ..utils.consts import provider_token, provider_live_token, currency
from .rating import ask_if_user_want_evaluate_the_product

from ..database.manipulation import (
    add_receipt_to_db,
    digital_product_was_purchased, physical_product_was_purchased)

from ..database.query import get_description_from_creator_id

from ..handlers.all_handlers import terms_callback

from .buttons import template_for_payment

from ..handlers.add_category import write_json_data_file

from ..utils.consts import users_key, product_key, creators_key, receipts_key, ui_key, new_product_key, pattern_to_save_everything

from ..templates.products import Sellable_Item, User, Receipt

from ..utils.log import logger

from ..utils.consts import *

#------------------------------------------------------------
def add_pre_checkout_query_to_chat_data(context, query):
    print('add_pre_checkout_query_to_chat_data()')
    context.chat_data["last_order"] = query

#------------------------------------------------------------
def check_terms_in_chat_data(update, context):
    print('check_terms_in_chat_data()')
    user_id = update.effective_user.id
    if context.bot_data[users_key][user_id].terms == False :
        terms_callback(update, context)
    # Rejected terms update
    return context.bot_data[users_key][user_id].terms

#------------------------------------------------------------
#  SEND PAID EFILE
#------------------------------------------------------------
def send_paid_efile(update, context):
    print('send_paid_efile()')

    user_chat_id = update.effective_chat.id
    document_id  = context.chat_data[product_key].actual().efile_id
    file_name = context.chat_data[product_key].actual().name
    caption_part_1 = 'Here is the file!'
    caption_part_2 = 'Please enjoy your purchase!'
    caption_text = '✨'+f'✨ {caption_part_1: ^30} ✨' + '✨\n\n' + f'{caption_part_2:^40}'
    context.bot.send_document(user_chat_id , document_id , caption = caption_text)

#------------------------------------------------------------
#------------------------------------------------------------
#  SEND INVOICE
#------------------------------------------------------------
def send_a_shipping_message(update, context, product , pattern_identifier):
    print(f'send_a_shipping_message()')
    logger.info(f'\n\n.... context.user_data ->  '+ str(context.user_data))
    logger.info(f'\n\n.... context.chat_data ->  '+ str(context.chat_data))
    logger.info(f'\n\n.... context.bot_data ->  '+ str(context.bot_data))

    user_id = update.effective_user.id
    if context.bot_data[users_key][user_id].terms == False :
        terms_callback(update, context)
        return

    # Minimum value for Stripe Payment to accept $1.36
    #  -> Assume anything lower than this is FREE
    if product.price < 136 :
        return send_paid_efile(update, context)

    title       = "A star is ready for you!💫"
    description = "Review the Invoice by Tapping 'Pay'.\n\nItem: \t" + product.name + '\n\n' + product.description

    # PAYLOAD: Bot-defined invoice payload. str 1- 128 bytes.
    # This will not be displayed to the user, use for your internal processes
    payload     = str(product.product_id)


    # Used for 'deep-linking' ->  turns link into /start @ botname payload
    start_parameter = "test-payment"

    item_price  = product.price

    max_tip_amount          = int(10 * item_price)
    suggested_tip_amounts   = [int(100), int(item_price/5), int(item_price/2)]

    labeled_prices = [LabeledPrice(product.name, product.price), LabeledPrice("Free Fee", int( 0 ))]


    protection  = False
    photoURL    = "https://i.imgur.com/BgCS7kf.jpeg"

    context.user_data.update({'checkout':product})

    context.bot.send_invoice(
        update.effective_chat.id, 
        title, 
        description, 
        payload, 
        provider_live_token,
        currency,
        labeled_prices,
        start_parameter,
        max_tip_amount = max_tip_amount,
        suggested_tip_amounts = suggested_tip_amounts,
        need_name = False,
        need_phone_number = False,
        need_email = False,
        need_shipping_address = product.shippable,
        protect_content = protection,
        photo_url = photoURL,
        photo_width = 161,
        photo_height = 100
        )

    desc_text = get_description_from_creator_id(product.creator_id)
    print(desc_text)
    context.bot.send_message(update.effective_chat.id, desc_text)

#------------------------------------------------------------
#  context.bot_data  is set to {} in this routine by PBT
def process_order(query, product):

    PROCESS_OK, PROCESS_FAIL = (True, False)

    if query.invoice_payload != str(product.product_id):
        return (PROCESS_FAIL, get_text("information_dont_match", context))

    try:
        logger.info(f'{query = }')
        return (PROCESS_OK, None)

    except:
        return (PROCESS_FAIL, get_text("error_in_orders", context))

#------------------------------------------------------------
#  PRE CHECKOUT
#------------------------------------------------------------
def pre_checkout_callback(update, context):
    print('pre_checkout_callback()')
    logger.info('update.pre_checkout_query' + str(update.pre_checkout_query))

    query = update.pre_checkout_query
    product = context.user_data['checkout']

    #  Dictionaries for context.chat_data are removed while in checkout mode
    (status, error_message) = process_order(query, product)

    if status:
        query.answer(ok=True)

    else:
        query.answer(ok=False, error_message=error_message)

#------------------------------------------------------------
pre_checkout_handler = PreCheckoutQueryHandler(pre_checkout_callback)

#------------------------------------------------------------
#  SUCCESSFUL PAYMENT
#------------------------------------------------------------
def successful_payment_callback(update, context):
    print('successful_payment_callback()')
    logger.info(f'{update.message.successful_payment = }   ->  '+ str(update.message.successful_payment))

    product         = context.user_data['checkout']
    checkout        = update.message.successful_payment
    sales_receipt   = product.generate_receipt(checkout)

    logger.info(f'{sales_receipt = }')

    context.bot_data[receipts_key].append(sales_receipt)
    add_receipt_to_db(*sales_receipt.db_values())

    if product.digital : digital_product_was_purchased(product.product_id)
    if not product.digital : physical_product_was_purchased(product.product_id)

    logger.info(f'\n\n.... context.bot_data ->  \n'+ str(context.bot_data))

    update.message.reply_text(get_text("successful_payment", context))

    send_paid_efile(update, context)

#------------------------------------------------------------
successful_payment_handler = MessageHandler(
    Filters.successful_payment, successful_payment_callback)
