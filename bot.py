#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

#  /usr/local/mysql/bin/mysql
#  alias mysql=/usr/local/mysql/bin/mysql
#  alias mysqladmin=/usr/local/mysql/bin/mysqladmin
#  mysql -u root --skip-password
#  SET GLOBAL wait_timeout = 1728000 ;
#     shell> cd /usr/local/mysql
#     shell> sudo ./bin/mysqld_safe
#     (ENTER YOUR PASSWORD, IF NECESSARY)
#     (PRESS CONTROL-Z)
#     shell> bg
#     (PRESS CONTROL-D OR ENTER "EXIT" TO EXIT THE SHELL)

import json
import pickle
import os
from pathlib import Path

import telegram

from telegram import Update, Chat, ChatMember, ChatMemberUpdated, ForceReply, BotCommand
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup


# Include text detection
from telegram.ext import Updater, Filters, CallbackContext, ContextTypes, JobQueue, BasePersistence, PicklePersistence
from telegram.ext import CallbackQueryHandler, ChatMemberHandler, CommandHandler,  ConversationHandler, InlineQueryHandler, MessageHandler, RegexHandler
from telegram.ext import ShippingQueryHandler, PreCheckoutQueryHandler

# From Inline Commands and From Inline Keyboards
from telegram.utils.helpers import escape_markdown

from telegram_ecommerce.database.db_wrapper import db
from telegram_ecommerce.utils.consts import credentials
from telegram_ecommerce.utils.log import logger
from telegram_ecommerce.handlers import all_public_commands_descriptions, all_handlers

token = credentials["token"]
admins = credentials["admins_username"]


#------------------------------------------------------------
#------------------------------------------------------------
#------------------------------------------------------------
def main():

    bot_name    = "FoxcoonIndustriesShopBot"

    bot         = telegram.Bot(token)

    data_path   = f'./docs/Data_Persistence_{bot_name}.pkl'
    data_dir    = Path(data_path)

    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    persistence_instance = PicklePersistence(filename = data_dir)

    updater = Updater(token, use_context = True, persistence = persistence_instance, arbitrary_callback_data = True)
    dp      = updater.dispatcher

    dp.bot.set_my_commands(all_public_commands_descriptions)

    for handler in all_handlers:
        dp.add_handler(handler)

    logger.info("bot started")
    updater.start_polling()
    updater.idle()
    db.close()
    logger.info("bot closed")


#------------------------------------------------------------
if __name__ == '__main__':
    main()


