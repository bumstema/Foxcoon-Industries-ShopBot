from telegram       import Update
from telegram.ext   import Updater, CallbackContext, ContextTypes



from ..templates.products       import User

from ..database.query           import user_exist, get_all_available_by_user_id, user_in_credentials_file
from ..database.manipulation    import create_account, create_account

from ..utils.log                import logger
from ..utils.consts             import users_key, product_key, creators_key, receipts_key, ui_key

products_data = {
    "name"               : "",
    "description"        : "",
    "unit_price"         : 0,
    "quantity_in_stock"  : 0,
    "quantity_purchased" : 0,
    "category_id"        : 0,
    "photo"              : None,
    "efile"              : None}


public_interface = { \
    'ui_message_id' : '',
    'ui_chat_id' : '',
    'last_message' : {},
    'view_product' : {} }
#------------------------------------------------------------
#------------------------------------------------------------
def initialize_bot(update, context) :
    logger.info(f'initialize_bot_data() ')

    if users_key in context.bot_data and ui_key in context.chat_data :
        logger.info(f'Bot_data already initialized.')
        return

    logger.info(f'bot_data -> ' + f'{context.bot_data = }')
    if users_key not in context.bot_data :
        logger.info(f'Bot_data has no "users_key" = ' + str(users_key) + '  data.')
        context.bot_data.setdefault(users_key, {})
        logger.info(f'bot_data -> ' + f'{context.bot_data = }')

    if receipts_key not in context.bot_data :
        context.bot_data.setdefault(receipts_key, [])

    if ui_key not in context.chat_data :
        context.chat_data.setdefault(product_key,{"products" : products_data})
        context.chat_data.setdefault(ui_key, public_interface)
        logger.info('chat_data -> ' + f'{context.chat_data = } \n')
    return

#------------------------------------------------------------
#------------------------------------------------------------
def initialize_user(update, context)  :
    logger.info(f'initialize_user_in_bot_data()')

    initialize_bot(update, context)
    user_id = update.effective_user.id
    username = update.effective_user.username

    if user_exist(user_id) :
        user_info = get_all_available_by_user_id(user_id)[0]
        logger.info(f'User found in DB with info:  ' + str(user_info))
        context.bot_data[users_key].update({user_id : User(user_info) })
        return

    logger.info('User not found in db' + str(context.bot_data[users_key]))
    if user_id not in list(context.bot_data[users_key]) :
        new_user =  User( (user_id, username, False, user_in_credentials_file(username)) )
        create_account(new_user)
        context.bot_data[users_key].update({user_id : new_user})
        logger.info(f'New User({user_id}, {username}) added to database!')
        logger.info(f'bot_data -> ' + f'{context.bot_data = }')
        return
