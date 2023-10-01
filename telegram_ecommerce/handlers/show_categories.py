from telegram import ReplyKeyboardRemove, InlineQueryResultArticle,     InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Filters,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    InlineQueryHandler)

#from ..templates.rating import
from ..language import get_text
from ..filters.decorators import execute_if_user_exist
from ..templates.buttons import template_for_show_a_list_of_products, get_list_of_buttons
from ..templates.buy_callbacks import send_a_shipping_message, send_paid_efile
from ..database.query import (
    get_all_available_by_category_name,
    get_name_of_all_categories, user_in_credentials_file)

from ..templates.products import (
    send_a_product,
    send_a_detailed_product,
    get_text_for_product,
    ListProductIterator)

from .all_handlers import sent_command_in_public, start, reset_memory

from ..handlers.add_category import write_json_data_file, read_json_data_file

from ..templates.products import Sellable_Item, User, Receipt

from ..utils.log import logger
from ..utils.consts import users_key, product_key, creators_key, receipts_key, ui_key, new_product_key, pattern_to_save_everything

from .add_users import initialize_user

from ..database.manipulation import delete_product_from_db_by

from ..utils.utils import float_from_user_input



import os.path

from pathlib import Path



# Include Character Identification
from uuid import uuid4
import re



(END                  ,
ASK_FOR_CATEGORY_NAME , 
GET_LIST_OF_PRODUCTS  ,
SHOW_LIST_OF_PRODUCTS ,
BUY_PROCESS           ,
IRL_SALES_TOKEN       ,
IRL_SALES_TOKEN_NAME  ,
IRL_SALES_TOKEN_PAID  ,
IRL_SALES_TOKEN_TYPE  ,
EDIT_PRODUCT            ) = range(-1, 9)




products_data = { product_key : []}




pattern_identifier = "pattern_"
PATTERN_TO_CATCH_THE_PREVIOUS_PRODUCT = 'previous_product'
PATTERN_TO_CATCH_THE_NEXT_PRODUCT = 'next_product'
PATTERN_TO_CATCH_THE_VIEW_DETAILS = 'product_details'
PATTERN_TO_CATCH_THE_BUY_BUTTON = 'buy_product'
PATTERN_TO_CATCH_THE_BACK_BUTTON = 'back_out'
PATTERN_TO_CATCH_THE_EDIT_PRODUCT = 'edit_product'
PATTERN_TO_CATCH_THE_DELETE_PRODUCT = 'delete_product'
PATTERN_TO_CATCH_THE_DOWNLOAD_BUTTON = 'download_product'
PATTERN_TO_CATCH_THE_GENERATE_IRL_SALE_BUTTON = 'generate_irl_sale_ticket'
PATTERN_TO_CATCH_THE_EDIT_PROPERTY = 'edit_property'
PATTERN_TO_CATCH_THE_COMMIT_EDIT = 'commit_edit'


#------------------------------------------------------------
#------------------------------------------------------------
def cancel_show_categories(update, context):
    print('cancel_show_categories()')
    delete_list_of_products(context.chat_data)
    query = update.callback_query
    if update.message:
        update.message.reply_text(
            get_text("cancelled_operation", context),
            reply_markup = ReplyKeyboardRemove()
            )
    elif query:
        query.edit_message_text(
            get_text("cancelled_operation", context),
            reply_markup = ReplyKeyboardRemove()
            )
    return END

#------------------------------------------------------------
def delete_list_of_products(chat_data):
    print('delete_list_of_products() ')
    chat_data[product_key] = {}

#------------------------------------------------------------
#  SHOW CATEGORIES
#------------------------------------------------------------
def ask_for_category_name( update, context ):
    print('ask_for_category_name()')

    if sent_command_in_public(update, context): return
    reset_memory(context)

    initialize_user(update, context)

    text = get_text("ask_for_category_name_of_the_product", context)
    name_of_all_categories = get_name_of_all_categories()
    if name_of_all_categories:
        send_a_inline_with_a_list_of_products(
            update, 
            context, 
            text,
            name_of_all_categories)
        return GET_LIST_OF_PRODUCTS
    else:
        update.message.reply_text(get_text("stock_empty", context))
        return END

#------------------------------------------------------------
def send_a_inline_with_a_list_of_products(update, context, text, list_of_names):
    logger.info('send_a_inline_with_a_list_of_products() ')
    buttons_with_list_of_names = get_list_of_buttons(*list_of_names)

    update.message.reply_text(text, reply_markup=buttons_with_list_of_names, parse_mode='MarkdownV2')

#------------------------------------------------------------
def load_products_in_chat_data( context, message ):
    print('save_products_in_chat_data() ')
    products_from_a_category_query = ( get_all_available_by_category_name(message) )
    products = ListProductIterator.create_a_list_from_a_query( products_from_a_category_query )
    context.chat_data.update({product_key: products})

#------------------------------------------------------------
def get_list_of_products(update, context):
    print('get_list_of_products()')

    category_name           = update.message.text
    name_of_all_categories  = get_name_of_all_categories()

    load_products_in_chat_data(context, category_name)

    if category_name not in name_of_all_categories:
        text = get_text("this_is_not_a_valid_category", context)
        update.message.reply_text(text)
        cancel_show_categories(update, context)
        return END

    if context.chat_data[product_key].is_empty():
        text = get_text( "without_product_in_this_category", context )
        update.message.reply_text( text )
        cancel_show_categories( update, context )
        return END

    text = get_text("OK", context)
    context.chat_data[ui_key].update({'last_message':update.message.reply_text(text, reply_markup=ReplyKeyboardRemove(), reply_to_message_id=None,allow_sending_without_reply=True)})
    logger.info(f'{context.chat_data[ui_key]}')

    show_list_of_products( update, context )

    return SHOW_LIST_OF_PRODUCTS

#------------------------------------------------------------
def show_list_of_products( update, context ):
    print('show_list_of_products()')
    logger.info(f'{context.chat_data  = }')

    product = context.chat_data[product_key].actual()

    logger.info(f'{product}')

    user_info = update.effective_user
    chat_info = update.effective_chat

    markup = template_for_show_a_list_of_products( pattern_identifier, context )
    text = get_text_for_product( product, context )

    context.chat_data[ui_key]['last_message'] = update.message.reply_photo( product.image_id,   caption = text, reply_markup=markup, parse_mode='MarkdownV2' )
    context.chat_data[ui_key]['ui_chat_id'] = context.chat_data[ui_key]['last_message']['chat']['id']
    context.chat_data[ui_key]['ui_message_id'] = context.chat_data[ui_key]['last_message']['message_id']

    print('UI CONFIGS:  \t'+str(context.chat_data[ui_key]['ui_chat_id'] )+ '  '+str( context.chat_data[ui_key]['ui_message_id'] ) )

    return SHOW_LIST_OF_PRODUCTS

#------------------------------------------------------------
#  SEND INVOICE
#------------------------------------------------------------
def send_a_shipping_message_callback(update, context):
    print('send_a_shipping_message_callback()')
    product = context.chat_data[product_key].actual()
    send_a_shipping_message(update, context, product, pattern_identifier)
    return END

#------------------------------------------------------------
#  BUTTON REPLIES
#------------------------------------------------------------
def catch_previous(update, context):
    print('catch_previous()')
    product = context.chat_data[product_key].previous()
    send_a_product(update, context, product, pattern_identifier)
    return SHOW_LIST_OF_PRODUCTS

#------------------------------------------------------------
def catch_details(update, context):
    print('catch_details()')
    product = context.chat_data[product_key].actual()
    send_a_detailed_product(update, context, product, pattern_identifier)
    return BUY_PROCESS

#------------------------------------------------------------
def catch_next(update, context):
    print('catch_next()')
    product = context.chat_data[product_key].next()
    send_a_product(update, context, product, pattern_identifier)
    return SHOW_LIST_OF_PRODUCTS

#------------------------------------------------------------
def catch_delete_product(update, context):
    print('catch_delete()')
    query = update.callback_query

    if 'delete' in query.data :
        logger.info(f'({query.data[7:-2] = })')
        name = query.data[7:-2]
        logger.info('delete_category(name)')
        text = 'Product Deleted from DB!'
    else:
        text = get_text("cancelled_operation", context)

    query.edit_message_text(text )
    return END

#------------------------------------------------------------
def catch_back(update, context):
    print('catch_back()')
    chat_id_saved = update.callback_query.message.chat.id
    ##  Removes the last message sent by the bot.
    context.bot.delete_message(
    chat_id=update.callback_query.message.chat.id, message_id=update.callback_query.message.message_id)
    return END

#------------------------------------------------------------
#  IRL SALES TOKEN
#------------------------------------------------------------
def catch_generate_irl_sales_token(update, context):
    logger.info('catch_generate_irl_sales_token()')
    text = "Enter the Telegram @ name of the user:"
    context.bot_data.setdefault('IRL_Token',{})
    logger.info(str(context.bot_data))
    chat_id_saved = update.callback_query.message.chat.id
    context.bot.send_message(text = text, chat_id = chat_id_saved)
    return IRL_SALES_TOKEN_NAME

#------------------------------------------------------------
def add_name_ask_amount_paid_for_irl_sales_token(update, context):
    logger.info('catch_generate_irl_sales_token()')
    username = update.message.text.replace('@','').replace(' ','')
    context.bot_data['IRL_Token'].update({'username':username})

    text = "How much was paid: "
    update.message.reply_text(text)

    return IRL_SALES_TOKEN_PAID

#------------------------------------------------------------
def add_amount_paid_ask_payment_type_for_irl_sales_token(update, context):

    try:
        amount_paid = update.message.text
        amount_paid = float_from_user_input(amount_paid)
        amount_paid = int( amount_paid * 100 )
        context.bot_data['IRL_Token'].update({'amount_paid':amount_paid})
        text = "What was the method of payment: "
        update.message.reply_text(text)
        return IRL_SALES_TOKEN_TYPE

    except:
        logger.info('update.message.text')
        text = "Error! Not a Number "
        update.message.reply_text(text)
        return IRL_SALES_TOKEN

#------------------------------------------------------------
def add_payment_type_send_irl_sales_token(update, context):
    payment_type = update.message.text
    context.bot_data['IRL_Token'].update({'payment_type':payment_type})

    product = context.chat_data[product_key].actual()
    irl_sales_receipt = product.generate_irl_sale(*context.bot_data['IRL_Token'].values())

    logger.info(f'{irl_sales_receipt = }')

    context.bot_data[receipts_key].append(irl_sales_receipt)

    irl_sales_receipt.save_to_db()
    irl_sales_receipt.update_sale_to_inventory(product.digital)

    text = '/sale_token@FoxcoonIndustriesShopBot '+str(irl_sales_receipt.transaction_id)
    update.message.reply_text(text)
    return END

#------------------------------------------------------------
#  EDIT PRODUCT
#------------------------------------------------------------
def catch_edit_product(update, context):
    logger.info('catch_edit_product()')
    text = "Select the property to edit:"
    print(str(Sellable_Item()))
    print(str( Sellable_Item().editable_properties()  ))
    keyboard = get_list_of_buttons( *Sellable_Item().editable_properties() )

    chat_id_saved = update.callback_query.message.chat.id
    context.bot.send_message(text = text, chat_id = chat_id_saved, reply_markup = keyboard)
    return EDIT_PRODUCT

#------------------------------------------------------------
def edit_property(update, context):
    logger.info('edit_property()')
    property_type =  update.message.text
    print('property_type : '+ str(property_type))
    # Catch Property to Edit
    # Send current property value
    product = context.chat_data[product_key].actual()
    print(product)
    print(product.name)

    text = str(dict(product).get(str(property_type)))
    print(text)
    # Ask what new value should be
    # Receive
    # Save in DB
    # Return to last GUI frame
    return PATTERN_TO_CATCH_THE_COMMIT_EDIT


#------------------------------------------------------------
#  Conversation Handler for /shop
#------------------------------------------------------------
show_categories_command = CommandHandler("shop",
    ask_for_category_name)

#------------------------------------------------------------
shop = ConversationHandler(
    entry_points = [show_categories_command],
    states = {
        ASK_FOR_CATEGORY_NAME : [
            MessageHandler(
                Filters.text, 
                ask_for_category_name)
            ],
        GET_LIST_OF_PRODUCTS : [
            MessageHandler(
                Filters.text, 
                get_list_of_products)
            ],
        SHOW_LIST_OF_PRODUCTS : [
            MessageHandler(
                Filters.text, 
                show_list_of_products
                ),
            CallbackQueryHandler(
                catch_next, 
                pattern = pattern_identifier +
                PATTERN_TO_CATCH_THE_NEXT_PRODUCT),
            CallbackQueryHandler(
                catch_previous, 
                pattern = pattern_identifier +
                PATTERN_TO_CATCH_THE_PREVIOUS_PRODUCT),
            CallbackQueryHandler(
                catch_details,
                pattern = pattern_identifier +
                PATTERN_TO_CATCH_THE_VIEW_DETAILS),
            CallbackQueryHandler(
                catch_back,
                pattern = pattern_identifier +
                PATTERN_TO_CATCH_THE_BACK_BUTTON),
            CallbackQueryHandler(
                catch_delete_product,
                pattern = pattern_identifier +
                PATTERN_TO_CATCH_THE_DELETE_PRODUCT)
            ],
        BUY_PROCESS : [
            CallbackQueryHandler(
                catch_previous, 
                pattern = pattern_identifier +
                PATTERN_TO_CATCH_THE_PREVIOUS_PRODUCT),
            CallbackQueryHandler(
                send_a_shipping_message_callback, 
                pattern = pattern_identifier + 
                PATTERN_TO_CATCH_THE_BUY_BUTTON),
            CallbackQueryHandler(
                send_paid_efile,
                pattern = pattern_identifier + 
                PATTERN_TO_CATCH_THE_DOWNLOAD_BUTTON),
            CallbackQueryHandler(
                catch_delete_product,
                pattern = pattern_identifier +
                PATTERN_TO_CATCH_THE_DELETE_PRODUCT),
            CallbackQueryHandler(
                catch_generate_irl_sales_token,
                pattern = pattern_identifier +
                PATTERN_TO_CATCH_THE_GENERATE_IRL_SALE_BUTTON ),
            CallbackQueryHandler(
                catch_edit_product,
                pattern = pattern_identifier +
                PATTERN_TO_CATCH_THE_EDIT_PROPERTY),
            CallbackQueryHandler(
                edit_property,
                pattern = pattern_identifier +
                PATTERN_TO_CATCH_THE_COMMIT_EDIT)
            ],
        EDIT_PRODUCT : [
            MessageHandler(
                Filters.text, 
                edit_property
                ),
            CallbackQueryHandler(
                edit_property,
                pattern = pattern_identifier +
                PATTERN_TO_CATCH_THE_COMMIT_EDIT)
            ],
        IRL_SALES_TOKEN : [
            MessageHandler(
                Filters.text, 
                catch_generate_irl_sales_token
                ),
            ],
        IRL_SALES_TOKEN_NAME : [
            MessageHandler(
                Filters.text, 
                add_name_ask_amount_paid_for_irl_sales_token
                ),
            ],
        IRL_SALES_TOKEN_PAID : [
            MessageHandler(
                Filters.text, 
                add_amount_paid_ask_payment_type_for_irl_sales_token
                ),
            ],
        IRL_SALES_TOKEN_TYPE : [
            MessageHandler(
                Filters.text, 
                add_payment_type_send_irl_sales_token
                ),
            ]
        },
    fallbacks = [MessageHandler(Filters.all, cancel_show_categories)],
    per_user=False,
    allow_reentry=True
    )

#------------------------------------------------------------
#  Inline Query to Sell Products
#------------------------------------------------------------
#------------------------------------------------------------
def inlinequery(update, CallbackContext) -> None:
    context = CallbackContext
    query = update.inline_query.query
    print('INLINEQUERY  ->  update  ->  '+str(update)+'\n')
    print('INLINEQUERY  ->  update.effective_chat  ->  '+str(update.effective_chat)+'\n')

    user_id : update.effective_user.id
    creators_list = get_name_of_all_categories()
    for names in creators_list :
        save_products_in_chat_data(context, names)

    products_creator_name_description = []
    for name_key in  context.chat_data['creators'].keys() :
        for item_key in context.chat_data['creators'][name_key]['products'] :
            products_creator_name_description.append((name_key, item_key[1], item_key[2] ))

    print('\nINLINEQUERY  ->  products_creator_name_description  ->  '+str(products_creator_name_description))
    print('\nINLINEQUERY  ->  CONTEXT.USER_DATA  ->  '+str(context.chat_data))
    results = garbageBoard(update, context, products_creator_name_description)

    update.inline_query.answer(results)
    print('INLINEQUERY  ->  results  ->  '+str(results))


#  Show list of actions for Inline Query
#------------------------------------------------------------
inline_query_command = InlineQueryHandler(inlinequery)

#------------------------------------------------------------
def garbageBoard(update, context, items) -> None:
    # Get List of Creators
    # creator_list
    # Populate gboard of creator names
    gboard = []
    for creator_item_descr in items :
        gboard.append(InlineQueryResultArticle( id=uuid4(), thumb_url="https://clipart-library.com/images/pTqrLABgc.jpg", title= str(creator_item_descr[1]), input_message_content = \
                                         InputTextMessageContent( 'ok'), description=str(creator_item_descr[2])))

    return gboard

#------------------------------------------------------------
def gboard_button(update, CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    print('Button Called \n')

    keyboard_choices = {    0 : 'Oops',
                            1 : 'Oops2',
                            2 : 'Oops3',
                            3 : 'No Links Selected'}
    print(keyboard_choices)
    print(query.data)
    print(keyboard_choices.get(query.data))
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery

    query.edit_message_text(text=keyboard_choices.get(query.data))
    query.answer()



#  Add function for keyboard button press (callbackquery)
#------------------------------------------------------------
gboard_button_command  = CallbackQueryHandler(gboard_button, pattern = 'inline')
