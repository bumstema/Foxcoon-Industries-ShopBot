from telegram import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Filters,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler)

from ..language import get_text
from ..templates.messages import ask_a_boolean_question
from ..templates.buttons import get_list_of_buttons
from ..utils.utils import float_from_user_input
from ..database.query import ( get_category_id_from_name, get_name_of_all_categories, get_category_id_from_creator_id)
from ..database.manipulation import (
    add_product as add_product_in_db,
    add_photo, add_efile)


from ..templates.products import Sellable_Item, User, Receipt

from ..utils.log    import logger
from ..utils.consts import users_key, product_key, creators_key, receipts_key, ui_key, new_product_key, pattern_to_save_everything

from .add_users import initialize_bot



from sqlitedict import SqliteDict


(END                        ,
START_ADD_PRODUCT           ,
ASK_FOR_PRODUCT_NAME        ,
ASK_FOR_PRODUCT_DESCRIPTION ,
ASK_FOR_PRODUCT_PRICE       ,
ASK_FOR_QUANTITY_IN_STOCK   ,
ASK_FOR_CATEGORY_NAME       ,
ASK_FOR_PRODUCT_PHOTO       ,
ASK_FOR_PRODUCT_EFILE       ,
REVIEW_PRODUCT_ENTRIES      ,
ASK_IF_ITS_ALL_OK           ) = range(-1, 10)


product_data = {
    "name"               : "",
    "description"        : "",
    "unit_price"         : 0,
    "quantity_in_stock"  : 0,
    "quantity_purchased" : 0,
    "category_id"        : 0,
    "photo"              : None,
    "efile"              : None}


creators_data_key = creators_key
product_data_key = product_key


(END                ,
EDIT_PRODUCT        ,
EDIT_NAME           ,
EDIT_DESCRIPTION    ,
EDIT_PRICE          ,
EDIT_SALE_PRICE     ,
EDIT_IN_STOCK       ,
EDIT_TOTAL_SOLD     ,
EDIT_PHOTO          ,
EDIT_EFILE          ,
EDIT_DIGITAL        ,
EDIT_SHIPPABLE       ) = range(-1, 11)



product_type = {"Digital Only": (True,False),"Phyiscal Item":(False,True)}




#------------------------------------------------------------
#  ADD PRODUCT - START FUNCTION
#------------------------------------------------------------
def start_add_product(update, context):
    logger.info(f'{context.chat_data = } ')
    context.chat_data[product_key] = product_data
    context.user_data.setdefault(new_product_key, Sellable_Item())

    logger.info(f'{context.user_data = } ')

    list_of_names = list(product_type)
    buttons_with_list_of_names = get_list_of_buttons(*list_of_names)
    text = 'Use the inline keyboard to select what kind of product this will be'
    update.message.reply_text(text, reply_markup=buttons_with_list_of_names, parse_mode='MarkdownV2')

    return START_ADD_PRODUCT

#------------------------------------------------------------
#  PUT FUNCTIONS
#------------------------------------------------------------
def put_product_name_in_data(context, name):
    logger.info('put_product_name_in_data()')
    context.chat_data[product_key]["name"] = name
    context.user_data[new_product_key].name = name
    return

#------------------------------------------------------------
def put_product_description_in_data(context, descr):
    logger.info('put_product_description_in_data()')
    context.chat_data[product_key]["description"] = descr
    context.user_data[new_product_key].description = descr
    return

#------------------------------------------------------------
def put_product_price_in_data(context, price):
    logger.info('put_product_price_in_data()')
    price = float_from_user_input(price)
    context.chat_data[product_key]["unit_price"] = price
    price = int( price * 100 )
    context.user_data[new_product_key].price = price
    return

#------------------------------------------------------------
def put_product_quantity_in_data(context, quantity):
    logger.info('put_product_quantity_in_data()')
    if int(quantity) <= 0 :
        context.user_data[new_product_key].digital = True

    context.chat_data[product_key]["quantity_in_stock"] = int(quantity)
    context.user_data[new_product_key].in_stock = int(quantity)
    return

#------------------------------------------------------------
def put_creator_id_in_data(context, effective_user):
    logger.info('put_creator_id_in_data()')
    category_id = get_category_id_from_name(effective_user.username)
    context.chat_data[product_key]["category_id"] = category_id
    
    context.user_data[new_product_key].creator_id = effective_user.id
    category_id = get_category_id_from_creator_id(effective_user.id)
    context.user_data[new_product_key].category_id = category_id
    return

#------------------------------------------------------------
def put_photo_in_data(update, context):
    logger.info('put_photo_in_data()')
    logger.info(f'{update.message.photo  =  }')
    photo = update.message.photo[0]
    photo = photo.get_file()
    context.chat_data[product_key]["photo"] = photo
    context.user_data[new_product_key].image_id = photo.file_id
    logger.info(f'Photo reference name: ' + str(context.chat_data[product_key]["photo"]))
    return

#------------------------------------------------------------
def put_efile_in_data(update, context):
    logger.info('put_efile_in_data()')
    logger.info('saving_efile_in_chat_data')
    logger.info(str(update.message.document))
    efile = update.message.document

    #  Download File
    efile_id = efile['file_id']
    context.chat_data[product_data_key]["efile"] = efile_id
    context.user_data[new_product_key].efile_id = efile_id
    logger.info(f'E-file reference name: ' + str(context.chat_data[product_data_key]["efile"]))
    return

#------------------------------------------------------------
#  ASK FUNCTIONS
#------------------------------------------------------------
def ask_for_product_name(update, context):
    logger.info('ask_for_product_name()')

    try:
        (digi,phys) = product_type[update.message.text]
        context.user_data[new_product_key].digital = digi
        context.user_data[new_product_key].physical = phys

        text = get_text("ask_for_product_name", context)
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ASK_FOR_PRODUCT_DESCRIPTION

    except:
        logger.info('invalid input: ' + str(update.message.text))
        update.message.reply_text('Invalid Type of Product')
        return END
        
#------------------------------------------------------------
#------------------------------------------------------------
def ask_for_product_description(update, context):
    logger.info('ask_for_product_description()')
    put_product_name_in_data(context, update.message.text)
    text = get_text("ask_for_product_description", context)
    update.message.reply_text(text)
    return ASK_FOR_PRODUCT_PRICE

#------------------------------------------------------------
#------------------------------------------------------------
def ask_for_product_price(update, context):
    logger.info('ask_for_product_price()')
    put_product_description_in_data(context, update.message.text)
    text = get_text("ask_for_product_price", context)
    update.message.reply_text(text)
    return ASK_FOR_QUANTITY_IN_STOCK

#------------------------------------------------------------
#------------------------------------------------------------
def ask_for_quantity_in_stock(update, context):
    logger.info('ask_for_quantity_in_stock()')
    try:
        put_product_price_in_data(context, update.message.text)
        text = get_text("ask_for_quantity_in_stock", context)
        update.message.reply_text(text)
        return ASK_FOR_CATEGORY_NAME
    except:
        text = get_text("this_is_not_a_number", context)
        update.message.reply_text(text)
        cancel_add_product(update, context)
        logger.info(f'{update.message.text = }')
        return END

#------------------------------------------------------------
#------------------------------------------------------------
def ask_for_category_name(update, context):
    logger.info('ask_for_category_name()')
    try:
        put_product_quantity_in_data(context, update.message.text)

        return ask_for_product_photo(update, context)
    except:
        text = get_text("this_is_not_a_integer", context)
        update.message.reply_text(text)
        cancel_add_product(update, context)
        return END

#------------------------------------------------------------
#------------------------------------------------------------
def ask_for_product_photo(update, context):
    logger.info('ask_for_product_photo()')
    try:
        put_creator_id_in_data(context, update.effective_user)
        text = get_text("ask_for_product_photo", context)
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ASK_FOR_PRODUCT_EFILE
    except:
        text = get_text("this_is_not_a_valid_category", context)
        update.message.reply_text(text)
        cancel_add_product(update, context)
        return END

#------------------------------------------------------------
#------------------------------------------------------------
def ask_for_product_efile(update, context):
    print('ask_for_product_efile()')
    try:
        put_photo_in_data(update, context)
        text = 'Send the document to sell:'
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ASK_IF_ITS_ALL_OK
    except:
        text = get_text("this_is_not_a_valid_category", context)
        update.message.reply_text(text)
        cancel_add_product(update, context)
        return END

#------------------------------------------------------------
#
#------------------------------------------------------------
def ask_if_its_all_ok(update, context):
    print('ask_if_its_all_ok()')
    try:
        put_efile_in_data(update, context)
        #save_photo_in_chat_data(update, context)
        ask_a_boolean_question(update, context, pattern_to_save_everything)
    except:
        text = get_text("error_when_storing_photo", context)
        update.message.reply_text(text)
        cancel_add_product(update, context)
        return END

#------------------------------------------------------------
#
#------------------------------------------------------------
def catch_response(update, context):
    logger.info('catch_response()')
    query = update.callback_query
    if query.data == pattern_to_save_everything + "OK":
        save_product_info_in_db(update, context)
        text = get_text("information_stored", context)
    else:
        text = get_text("cancelled_operation", context)

    query.edit_message_text(text)

    return END

#------------------------------------------------------------
def cancel_add_product(update, context):
    logger.info('Removing last entered data')
    context.chat_data[product_key].clear()
    context.user_data[new_product_key].clear()
    text = get_text("cancelled_operation", context)
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    return END

#------------------------------------------------------------
#  SAVE - SQL DATABASE
#------------------------------------------------------------
def save_product_info_in_db(update, context):
    print('save_product_info_in_db()')

    product_data = context.chat_data[product_data_key] 
    photo = product_data["photo"]
    add_photo(
        photo.file_id,
        photo.download_as_bytearray())
    efile = product_data["efile"]
    product_info = context.user_data[new_product_key].tuple_for_database()
    logger.info('Tuple for database saving:  ' + str(product_info))
    add_product_in_db( *product_info )
    return
#------------------------------------------------------------
#------------------------------------------------------------
#  SAVE - SQLITE3 DICTIONARY
#------------------------------------------------------------

def save_product_info_in_sqlite3(update, context):
    creator_id = update.effective_user.id
    item = context.user_data[new_product_key]
    logger.info(f'{context.bot_data = }')
    logger.info(f'{context.user_data = }')

    sqlite_save('bot_data', context.bot_data)
    logger.info(f'SQLITE file saved!')

#------------------------------------------------------------
#
#  To look at .sqlite3 files from command line :
#          $> sqlite3 db_name.sqlite
#     sqlite> .dump
#
#------------------------------------------------------------
def sqlite_save(key, value, cache_file="cache.sqlite3"):
    try:
        with SqliteDict(cache_file) as mydict:
            mydict[key] = value
            mydict.commit()
    except Exception as ex:
        logger.info(f"Error with sqlite save. {ex}")

#------------------------------------------------------------
def sqlite_load(key, cache_file="cache.sqlite3"):
    try:
        with SqliteDict(cache_file) as mydict:
            value = mydict[key]
        return value
    except Exception as ex:
        logger.info(f"Error with sqlite load. {ex}")

#------------------------------------------------------------
#------------------------------------------------------------
#  COMMAND HANDLER - ADD PRODUCT
#------------------------------------------------------------
add_product_command = (
    CommandHandler("add_product", start_add_product))

#------------------------------------------------------------
add_product = ConversationHandler(
    entry_points = [add_product_command],
    states = {
        START_ADD_PRODUCT : [
            MessageHandler(
                Filters.text,
                ask_for_product_name)
            ],
        ASK_FOR_PRODUCT_DESCRIPTION : [
            MessageHandler(
                Filters.text,
                ask_for_product_description)
            ],
        ASK_FOR_PRODUCT_PRICE : [
            MessageHandler(
                Filters.text, 
                ask_for_product_price)
            ],
        ASK_FOR_QUANTITY_IN_STOCK : [
            MessageHandler(
                Filters.text, 
                ask_for_quantity_in_stock)
            ],
        ASK_FOR_CATEGORY_NAME : [
            MessageHandler(
                Filters.text, 
                ask_for_category_name)
            ],
        ASK_FOR_PRODUCT_PHOTO : [
            MessageHandler(
                Filters.text, 
                ask_for_product_photo)
            ],
        ASK_FOR_PRODUCT_EFILE : [
            MessageHandler(
                Filters.photo,
                ask_for_product_efile)
            ],
        ASK_IF_ITS_ALL_OK : [
            MessageHandler(
                Filters.document,
                ask_if_its_all_ok),
            CallbackQueryHandler(
                catch_response,
                pattern=pattern_to_save_everything
                )
            ]
        },
    fallbacks = [MessageHandler(Filters.all, cancel_add_product)]
    )
