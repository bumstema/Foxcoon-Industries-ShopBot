from telegram.ext import CommandHandler,  CallbackQueryHandler, CallbackContext
from telegram import Update, Chat, ChatMember, ChatMemberUpdated, ForceReply, ReplyKeyboardRemove

# Include text detection
from telegram.ext import Updater, Filters, CallbackContext, ContextTypes, JobQueue
from telegram.ext import CallbackQueryHandler, ChatMemberHandler, CommandHandler,  ConversationHandler, InlineQueryHandler, MessageHandler, RegexHandler

# From Inline Commands and From Inline Keyboards
from telegram.utils.helpers import escape_markdown
from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup

from .add_category import write_json_data_file


from ..language import get_text
from ..database.query import is_admin, get_all_descriptions_from_all_creators, get_efile_id_from_product_id, customers_names_from_receipts_by_product_id, username_from_user_id
from ..database.manipulation import set_terms_true
from ..utils.consts import users_key, product_key, creators_key, receipts_key, ui_key, new_product_key, pattern_to_save_everything

from ..templates.products import Sellable_Item, User, Receipt
from .add_users import initialize_user

from ..utils.log import logger

# import urllib library
from urllib.request import urlopen
from PIL import Image
import requests
from io import BytesIO


#------------------------------------------------------------
#   CHECK: SENT_COMMAND_IN_PUBLIC
#------------------------------------------------------------
def sent_command_in_public(update, context):
    return False
    if update.effective_chat.type != 'private' :
        text_reply = 'Thank you for the command.🤗\nI work best in Private Message, so I hope you don\'t mind me sliding into your DM\'s. 😏'
        update.message.reply_text(text_reply)
        chat_id_saved = update.effective_user.id
        text_reply = '⭐️ Good Marfing!🎉 \n🖥 You sent a command from:\n"'+str(update.effective_chat.title)+'"!'+ '\n\n'+ 'It\'s time to /start the ShopBot!'
        context.bot.send_message(text = text_reply, chat_id = chat_id_saved )
        return True
    return False

#------------------------------------------------------------
#  Remove Data from Memory
#------------------------------------------------------------
def reset_memory(context):
    context.user_data.clear()
    context.chat_data.clear()
    return

#------------------------------------------------------------
#   START
#------------------------------------------------------------
def start_callback(update, context):
    if sent_command_in_public(update, context):
        return

    reset_memory(context)
    text = get_text("start", context)
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

#------------------------------------------------------------
start = CommandHandler("start", start_callback)

#------------------------------------------------------------
#   START - DEEPLINK "verify"
#------------------------------------------------------------
VERIFIED_PURCHASE = "verify"

def start_irl_sale_verification(update, context):
    initialize_user(update, context)


    try :
        token = context.args[0]
        logger.info(str(token))

        for index, receipt in enumerate(context.bot_data[receipts_key]) :
            logger.info(str(receipt))
            if receipt.transaction_id == token:
                receipt_index = index
                logger.info('INDEX FOUND')

        val = context.bot_data[receipts_key][receipt_index].verify_irl_sale(update.effective_user)
        logger.info(str(val))
        text = "🏷 Accepted Token! Sending Product!💫"
        context.bot.send_message(update.effective_user.id, text)

        verified_receipt = context.bot_data[receipts_key][receipt_index]
        logger.info('----verified' + str(verified_receipt))
        document_id = get_efile_id_from_product_id(verified_receipt.product_id)
        logger.info(str(document_id))
        context.bot.send_document(update.effective_chat.id , document_id , caption = "✨ Thank you!", reply_markup=ReplyKeyboardRemove())

    except:
        #   token not in receipts, invalid token
        update.message.reply_text("Unverified Token :<", reply_markup=ReplyKeyboardRemove())

#------------------------------------------------------------
irl_sales_command = CommandHandler("sale_token", start_irl_sale_verification)

#------------------------------------------------------------
#   TERMS AND CONDITIONS
#------------------------------------------------------------
TERMS_ACCEPTED, TERMS_REJECTED = ['terms_accept','terms_reject']

#------------------------------------------------------------
def terms_callback(update, context):
    print('terms_callback()')
    
    text = get_text("terms", update)
    user_id = update.effective_user.id
    context.bot.send_message(user_id ,text + '\n\n' + 'Do you Accept or Reject the terms?', reply_to_message_id= False, reply_markup=terms_keyboard() )
    return

#------------------------------------------------------------
terms_command = CommandHandler("terms", terms_callback)

#------------------------------------------------------------
def terms_keyboard():
    keyboard_button_accept =  InlineKeyboardButton('✅ Accept', callback_data=TERMS_ACCEPTED)
    keyboard_button_reject =  InlineKeyboardButton('❌ Reject', callback_data=TERMS_REJECTED)
    terms_keyboard = [[keyboard_button_accept, keyboard_button_reject]]
    terms_keyboard_markup = InlineKeyboardMarkup(terms_keyboard)
    return terms_keyboard_markup

#------------------------------------------------------------
def terms_selector(update: Update, context: CallbackContext) -> None:
    print('terms_selector()')

    query = update.callback_query
    user_id = update.effective_user.id

    if query.data == TERMS_ACCEPTED :
        context.bot_data[users_key][user_id].terms = True
        set_terms_true(user_id)

    message = {TERMS_REJECTED : 'Terms: Rejected', TERMS_ACCEPTED :'Terms: Accepted'}
    query.edit_message_text( text= message.get(query.data))
    query.answer()
    return

#------------------------------------------------------------
terms_button = CallbackQueryHandler(terms_selector, pattern = 'terms')

#------------------------------------------------------------
#   CREATOR INFO
#------------------------------------------------------------
def creator_info_callback(update, context):
    text = get_text("creator_info", update)
    descriptions = get_all_descriptions_from_all_creators()
    print(str(descriptions))
    for descr in descriptions : text += descr[0]
    update.message.reply_text(text)

#------------------------------------------------------------
creator_info_command = CommandHandler("creator_info", creator_info_callback)

#------------------------------------------------------------
#   PAYMENT INFO
#------------------------------------------------------------
def payment_info_callback(update, context):
    text = get_text("payment_info", update)
    update.message.reply_text(text)

#------------------------------------------------------------
payment_info_command = CommandHandler("payment_info", payment_info_callback)

#------------------------------------------------------------
#   SUPPORT
#------------------------------------------------------------
def support_callback(update, context):
    text = get_text("support", update)
    update.message.reply_text(text)

#------------------------------------------------------------
support_command = CommandHandler("support", support_callback)

#------------------------------------------------------------
#   HELP
#------------------------------------------------------------
def help_callback(update, context):
    text = get_text("help", update)
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

#------------------------------------------------------------
help_command = CommandHandler("help", help_callback)

#------------------------------------------------------------
#   CANCEL
#------------------------------------------------------------
def cancel_callback(update, context):
    update.message.reply_text("I'm cancelling you on twitter!", reply_markup=ReplyKeyboardRemove())

#------------------------------------------------------------
cancel_command = CommandHandler("cancel", cancel_callback)

#------------------------------------------------------------
#   SALES STATS
#------------------------------------------------------------
#------------------------------------------------------------
def sales_username_from_receipts(update, context):
    customers_names_by_product_id(product_id)
    username_from_user_id(user_id)
    return

#------------------------------------------------------------
def buyer_name_from_id(user_id):
    if user_id != 0 :
        name = username_from_user_id(user_id)
    else:
        name = f'cash'
    return name

#------------------------------------------------------------
def sales_stats_callback(update, context):
    full_receipts = context.bot_data[receipts_key]
    sales_total_paid = 0
    number_of_sales = 0
    product_and_buyer_ids = {}
    product_and_usernames = {}

    # product_and_buyer_ids can be removed
    for sale in full_receipts:
        product_and_buyer_ids.setdefault(sale.product_id,[])
        product_and_buyer_ids[sale.product_id].append(sale.buyer_id)

        product_and_usernames.setdefault(sale.product_id,[])
        product_and_usernames[sale.product_id].append(buyer_name_from_id(sale.buyer_id))

        if sale.creator_id == update.effective_user.id:

            sales_total_paid    += sale.total_paid
            number_of_sales     += 1

    text = "For Creator ⭐️" + str(update.effective_user.username) +"⭐️\n\n" +\
            "💵\t Total: \t$ " + f'{sales_total_paid/100:.2f}' + "\n" +\
            "📚\t Sales: \t" + str(number_of_sales) + "\n\n"

    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

    text = f'Product Number - Buyers \n\n'
    for prdct, usr in product_and_usernames.items():
        text += f'{prdct}\t : \t'
        for name in usr :
            text += f'{name}, \t'
        text += f'\n\n'
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

#------------------------------------------------------------
sales_stats_command = CommandHandler("sales_stats", sales_stats_callback)
