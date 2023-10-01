from telegram import BotCommand

from ..language import get_text
from .language import language
from .register import register
from .add_category import add_category, delete_category, cancel_command
from .add_product import add_product 
from .show_categories import shop, inline_query_command, gboard_button_command
from .search import search
from .all_handlers import start,irl_sales_command,help_command,payment_info_command, support_command, terms_command, creator_info_command, terms_button,sales_stats_command, cancel_command
from ..templates.rating import rating_precess_handlers
from ..templates.buy_callbacks import (
    pre_checkout_handler,
    successful_payment_handler)
#------------------------------------------------------------
#------------------------------------------------------------
all_handlers = ([
    start,
    irl_sales_command,
    help_command,
    cancel_command,
    register,
    add_category,
    delete_category,
    cancel_command,
    add_product, 
    language,
    search,
    shop,
    pre_checkout_handler, 
    successful_payment_handler,
    payment_info_command,
    support_command,
    terms_command,
    inline_query_command,
    gboard_button_command,
    creator_info_command,
    sales_stats_command] +
    rating_precess_handlers +
    [terms_button]
    )


#------------------------------------------------------------
#------------------------------------------------------------
all_public_commands_descriptions = [
    BotCommand(
        "start", 
        get_text("start_description")
        ),
    BotCommand(
        "shop", 
        get_text("show_categories_description")
        ),
    BotCommand(
        "ai_art",
        f"Enter the page number to see the solution! (/ai_art page)"
        )
    ]
