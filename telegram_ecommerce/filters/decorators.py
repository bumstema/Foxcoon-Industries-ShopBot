from ..language import get_text
from ..database.query import (
    user_exist,
    is_admin)


END = -1



#------------------------------------------------------------
def first_use_of_bot_does_user_exist(callback):
    def wapper_does_user_exist(update, context):
        user_id = update.effective_user.id
        uuids = context.bot_data['all_users'].keys()
        if user_id not in uuids:
            return

        else:
            return callback(update, context)
    return wapper_does_user_exist

#------------------------------------------------------------
def warning_the_user_that_already_have_an_account(update, context):
    text = get_text("user_have_account", context)
    update.message.reply_text(text)
    return END

#------------------------------------------------------------
def warning_user_does_not_have_an_account(update, context):
    text = get_text("user_dont_have_account", context)
    update.message.reply_text(text)
    return END

#------------------------------------------------------------
def execute_if_user_exist(callback):
    def execute_warning_if_user_dont_exist(update, context):
        user_id = update.effective_user.id
        if user_exist(user_id):
            return callback(update, context)

        else:
            return warning_user_does_not_have_an_account(
                update, context)
    return execute_warning_if_user_dont_exist

#------------------------------------------------------------
def execute_if_user_dont_exist(callback):
    def execute_warning_if_user_exist(update, context):
        user_id = update.effective_user.id
        if user_exist(user_id):
            return warning_the_user_that_already_have_an_account(
                update, context)
        else:
            return callback(update, context)
    return execute_warning_if_user_exist
