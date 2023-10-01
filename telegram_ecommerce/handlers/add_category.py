import json

from telegram import ReplyKeyboardRemove

from telegram.ext import (
    Filters,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler)

from ..language import get_text
from ..templates.messages import ask_a_boolean_question
from ..database.manipulation import (
    add_category as add_category_in_db, update_category_description,
    add_photo)
from ..database.manipulation import delete_category_from_db

from ..templates.buttons import get_list_of_buttons

from ..database.query import (
    get_category_id_from_name, get_description_from_creator_id,
    get_name_of_all_categories)

from ..utils.log import logger

from .add_users import initialize_user

from ..utils.consts import users_key, product_key, creators_key, receipts_key, ui_key, new_product_key, pattern_to_save_everything

from ..templates.products import Sellable_Item, User, Receipt, Creator


(END                         ,
ASK_FOR_CATEGORY_DESCRIPTION ,
ASK_FOR_CATEGORY_TAGS        ,
ASK_FOR_CATEGORY_PHOTO       ,
ASK_IF_ITS_ALL_OK            ,
ASK_IF_ITS_OK_TO_DELETE         ) = range(-1, 5)



category_data = {
    "username"  : "",
    "info"      : "",
    "id"        : ""
    }


#------------------------------------------------------------
def put_category_data_in_chat_data(chat_data):
    chat_data[creators_key] = category_data

#------------------------------------------------------------
def delete_category_data_from_chat_data(chat_data):
    chat_data[creators_key] = {}

#------------------------------------------------------------
def save_name_in_chat_data(chat_data, name):
    chat_data[creators_key]["username"] = name

#------------------------------------------------------------
def save_description_in_chat_data(chat_data, description):
    chat_data[creators_key]["info"] = description

#------------------------------------------------------------
def save_telegram_id_in_chat_data(chat_data, telegram_id):
    chat_data[creators_key]["id"] = telegram_id
    
#------------------------------------------------------------
def update_db_flag(context):
    context.user_data.update({"update_db": True})
    print(context.user_data)
    
#------------------------------------------------------------
def save_category_info_in_db(update, context):
    logger.info(str(context.chat_data))

    print(context.user_data)
    if context.user_data['update_db'] :
        print('updating db')
        update_category_description(update.effective_user.id, context.chat_data[creators_key]["info"])
        print('db updated')
        context.user_data.pop('update_db')
        return

    category_data = context.chat_data[creators_key]

    new_creator = Creator(category_data)
    if creators_key not in context.bot_data:
        context.bot_data.setdefault(creators_key,[new_creator])

    else:
        context.bot_data[creators_key].append([new_creator])

    if receipts_key not in context.bot_data :
        context.bot_data.setdefault(receipts_key, [])
        
    add_category_in_db(
        category_data["username"],
        category_data["id"],
        category_data["info"])

#------------------------------------------------------------
def ask_for_category_description(update, context):

    initialize_user(update, context)

    telegram_id = update.effective_user.id
    username    = str(update.effective_user.username)

    if not context.bot_data[users_key][telegram_id].is_creator :
        return

    put_category_data_in_chat_data(context.chat_data)

    save_telegram_id_in_chat_data(context.chat_data, telegram_id)
    save_name_in_chat_data(context.chat_data, username)

    # If info already in database, prompt to edit
    try:

        desc = get_description_from_creator_id(telegram_id)

        update_db_flag(context)

        text = f'Current Creator Info Detected! \nUsername: {username} \nTelegram_id: {telegram_id}'
        text += f'\nDescription:\t{desc}\n\n'
        update.message.reply_text(text)
        text = f'Write and send a new description to be updated:'
        update.message.reply_text(text)

    except:

        text = 'New Creator Successfully Detected! \n\nUsername: '+ username +'\nTelegram_id: ' + str(telegram_id)
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        text = get_text("ask_for_category_description", context)
        update.message.reply_text(text)

    return ASK_IF_ITS_ALL_OK

#------------------------------------------------------------
def ask_if_its_all_ok(update, context):
    try:
        save_description_in_chat_data(context.chat_data, update.message.text)
        ask_a_boolean_question(update, context, pattern_to_save_everything)
    except:
        cancel_add_category(update, context)
        return END

#------------------------------------------------------------
def catch_response(update, context):
    query = update.callback_query
    if query.data != pattern_to_save_everything + "OK":
        text = get_text("cancelled_operation", context)
        query.edit_message_text(text)
        return END

    try:
        save_category_info_in_db(update, context)
        text = get_text("information_stored", context)
    except:
        text = get_text("cancelled_operation", context)

    query.edit_message_text(text)
    return END

#------------------------------------------------------------
def cancel_add_category(update, context):
    delete_category_data_from_chat_data(context.chat_data)

    text = 'Cancelled Operation.'
    saved_message = update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    logger.info('Message: ' + str(saved_message))
    update.message.delete()
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    return END

#------------------------------------------------------------
cancel_command = (
    CommandHandler("cancel", cancel_add_category))

#------------------------------------------------------------
def pick_from_all_category_names(update, context):
    try:
        text = 'Select a Creator to Remove: '
        buttons_with_list_of_all_names = ( get_list_of_buttons(*(get_name_of_all_categories() ) ) )
        update.message.reply_text( text, reply_markup=buttons_with_list_of_all_names)
        return ASK_IF_ITS_OK_TO_DELETE
    except:
        text = 'Error with picking from the list of creators'
        update.message.reply_text(text)
        cancel_add_category(update, context)
        return END

#------------------------------------------------------------
def ask_if_ok_to_delete(update, context):
    try:
        logger.info(str(context.chat_data))
        logger.info(str(update.message.text))
        text = 'Deleting: ' + str(update.message.text)
        print(text)
        update.message.reply_text(text)
        ask_a_boolean_question(update, context, 'delete ' + update.message.text , question='Yes or No?')
    except:
        text = 'Error with asking to delete creator'
        update.message.reply_text(text)
        cancel_add_category(update, context)
        return END

#------------------------------------------------------------
def catch_delete_response(update, context):
    query = update.callback_query
    logger.info('query : ' + str(query.data))
    if 'delete' in query.data :
        print(f'({query.data[7:-2] = })')
        name = query.data[7:-2]
        print('delete_category(name)')
        delete_category_from_db(name)
        text = 'Creator Deleted from DB!'
    else:
        text = get_text("cancelled_operation", context)
    query.edit_message_text(text )
    return END

#------------------------------------------------------------
#------------------------------------------------------------
delete_category_command = (
    CommandHandler("delete_creator", pick_from_all_category_names))

#------------------------------------------------------------
delete_category = ConversationHandler(
    entry_points = [delete_category_command],
    states = {
        ASK_IF_ITS_OK_TO_DELETE : [
            MessageHandler(
                Filters.text,
                #Filters.photo,
                ask_if_ok_to_delete),
            CallbackQueryHandler(
                catch_delete_response,
                pattern='delete'
                )
            ]
        },
    fallbacks = [MessageHandler(Filters.all, cancel_add_category)]
    )

#------------------------------------------------------------
#------------------------------------------------------------
add_category_command = (
    CommandHandler("add_creator", ask_for_category_description))

#------------------------------------------------------------
add_category = ConversationHandler(
    entry_points = [add_category_command],
    states = {
        ASK_FOR_CATEGORY_DESCRIPTION : [
            MessageHandler(
                Filters.text, 
                ask_for_category_description)
            ],
        ASK_IF_ITS_ALL_OK : [
            MessageHandler(
                Filters.text,
                #Filters.photo,
                ask_if_its_all_ok),
            CallbackQueryHandler(
                catch_response,
                pattern=pattern_to_save_everything
                )
            ]
        },
    fallbacks = [MessageHandler(Filters.all, cancel_add_category)]
    )

#------------------------------------------------------------
#------------------------------------------------------------
# Using a JSON string
def write_json_data(data) :
    # Directly from dictionary
    with open('json_telegram_ecommerce_creator_data_' + str(data[creators_key]["name"]) +'.json', 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4)
        print('JSON SAVED : ' + f'({data = })')
        
#------------------------------------------------------------
def read_json_data() :
    with open('json_telegram_ecommerce_product_data.json') as json_file:
        temp = json.load(json_file)
        print('JSON LOADED : ' + str(temp))
    return(temp)

#------------------------------------------------------------
# Using a JSON string
def write_json_data_file(data, filename) :
    # Directly from dictionary
    with open('docs/'+str('FoxcoonIndustriesShopBot')+'.context.'+ filename + '.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)
        print('JSON SAVED to '+str('FoxcoonIndustriesShopBot')+'_'+str(filename)+'.json   : ' + f'({data = })')


#------------------------------------------------------------
def read_json_data_file(filename) :
    with open('docs/'+str('FoxcoonIndustriesShopBot')+'.context.'+ filename + '.json', 'r')  as json_file:
        temp = json.loads(json_file)
        print('JSON LOADED  '+str('FoxcoonIndustriesShopBot')+'_'+str(filename)+'.json   : ' + str(temp))
    return(temp)

#------------------------------------------------------------
#------------------------------------------------------------
