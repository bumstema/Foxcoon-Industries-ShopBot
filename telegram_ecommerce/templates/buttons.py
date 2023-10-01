
from telegram import (
    KeyboardButton as Button,
    ReplyKeyboardMarkup,
    InlineKeyboardButton as InlineButton,
    InlineKeyboardMarkup)

from ..database.query import user_in_credentials_file

from ..utils.consts import BAD_RATING, REGULAR_RATING, GOOD_RATING
from ..language import get_text

from ..utils.consts import *

#------------------------------------------------------------
def boolean_question(pattern_identifier, context=None):
    print('boolean_question()')

    return InlineKeyboardMarkup([
        [
            InlineButton(get_text("cancel", context), 
                callback_data=pattern_identifier + 'cancel'),
            InlineButton(get_text("OK", context), 
                callback_data=pattern_identifier + 'OK')
        ]
    ])

#------------------------------------------------------------
def rating_template(pattern_identifier, context=None):
    print('rating_template()')
    return InlineKeyboardMarkup([
        [
            InlineButton(get_text("bad", context), 
                callback_data=pattern_identifier + str(BAD_RATING))
        ],
        [
            InlineButton(get_text("regular", context), 
                callback_data=pattern_identifier + str(REGULAR_RATING))
        ],
        [
            InlineButton(get_text("good", context), 
                callback_data=pattern_identifier + str(GOOD_RATING))
        ]
    ])

#------------------------------------------------------------
def numeric_keyboard(pattern_identifier, context=None):
    return (InlineKeyboardMarkup([
    [
        InlineButton("1", callback_data=pattern_identifier + 'digit_1'),
        InlineButton("2", callback_data=pattern_identifier + 'digit_2'),
        InlineButton("3", callback_data=pattern_identifier + 'digit_3')
    ],
    [
        InlineButton("4", callback_data=pattern_identifier + 'digit_4'),
        InlineButton("5", callback_data=pattern_identifier + 'digit_5'),
        InlineButton("6", callback_data=pattern_identifier + 'digit_6')
    ],
    [
        InlineButton("7", callback_data=pattern_identifier + 'digit_7'),
        InlineButton("8", callback_data=pattern_identifier + 'digit_8'),
        InlineButton("9", callback_data=pattern_identifier + 'digit_9')
    ],
    [
        InlineButton(get_text("cancel", context), 
            callback_data=pattern_identifier + 'cancel_numeric_keyboard'),
        InlineButton("0", callback_data=pattern_identifier + 'digit_0'),
        InlineButton(get_text("next", context), 
            callback_data=pattern_identifier + 'end_numeric_keyboard')
    ]]))

#------------------------------------------------------------
def login_keyboard(pattern_identifier, context=None): 
    return ({
    "step_1": InlineKeyboardMarkup([
    [
        InlineButton(get_text("cancel", context), 
            callback_data=pattern_identifier + 'cancel_loging_process'),
        InlineButton(get_text("next", context), 
            callback_data=pattern_identifier + 'next_step_1_login_process'),
    ]]),
    "step_2": numeric_keyboard(pattern_identifier, context),
    "step_3": InlineKeyboardMarkup([
    [
        InlineButton(get_text("cancel", context),
            callback_data=pattern_identifier + 'cancel_loging_process'),
        InlineButton(get_text("next", context),
            callback_data=pattern_identifier + 'end_login_process'),
    ]]) })

#------------------------------------------------------------
def get_list_of_buttons(*names_in_buttons):
    print('get_list_of_buttons()')
    list_of_buttons = []
    for name_of_the_button in names_in_buttons:
        list_of_buttons.append(
            [
                Button(str(name_of_the_button) )
            ]
        )
    return ReplyKeyboardMarkup(list_of_buttons)

#------------------------------------------------------------
def template_for_show_a_list_of_products(pattern_identifier, context):
    print('template_for_show_a_list_of_products()')
    print('\t'+str(context.chat_data))
    buttons_arrangement = [
        [   InlineButton(
                "🔙",
                callback_data=pattern_identifier + 'back_out'),
            InlineButton(
                "⬅️ Prev",
                callback_data=pattern_identifier + 'previous_product'),
            InlineButton(
                "⬆️ View",
                callback_data=pattern_identifier + 'product_details'),
            InlineButton(
                "➡️ Next",
                callback_data=pattern_identifier + 'next_product')
    ]]
       
    kb =  InlineKeyboardMarkup(buttons_arrangement)
    return(kb)

#------------------------------------------------------------
def template_for_show_a_detailed_product(pattern_identifier, update, context):
    print('template_for_show_a_detailed_product()')
    buy_button      = InlineButton("⭐️ Buy", callback_data=pattern_identifier + 'buy_product')
    back_button     = InlineButton("🔙", callback_data=pattern_identifier + 'previous_product')
    download_button = InlineButton("⤵️ Download", callback_data=pattern_identifier + 'download_product')
    edit_button = InlineButton("📝 Edit", callback_data=pattern_identifier + 'edit_property')
    irl_button      = InlineButton("🏷 Generate IRL Sales Ticket", callback_data=pattern_identifier + 'generate_irl_sale_ticket')

    buttons_arrangement =[  [ back_button, buy_button ]]

    product_id = context.chat_data['current_product'].product_id
    user_id = update.effective_user.id
    creator_id = context.chat_data['current_product'].creator_id
    print('\nbot_data -> ' + str(context.bot_data))


    for sale in context.bot_data[receipts_key]:
        if (user_id  == sale.buyer_id and sale.product_id == product_id) and (user_id != creator_id ):
            buttons_arrangement.append([download_button])
            break

    if user_id == creator_id:
        buttons_arrangement.append([edit_button])
        buttons_arrangement.append([download_button])
        buttons_arrangement.append([irl_button])

    return InlineKeyboardMarkup(buttons_arrangement)

#------------------------------------------------------------
def template_for_payment(pattern_identifier,context):
    buttons_arrangement =[ \
        InlineButton("💳 Pay", pay=True)]
        
    return InlineKeyboardMarkup(buttons_arrangement)
