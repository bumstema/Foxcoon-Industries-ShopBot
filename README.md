# telegram_ecommerce
A framework for building a Telegram bot that acts as an online platform for selling digital items directly to users within the app.



The bot requires a SQL database to store seller info/items and customer sales data.  Payments are processed via Stripe.  To obtain a sales token, messasge @BotFather on Telegram.


Place sensitive connection info (such as bot tokens and sql login info) into: telegram_ecommerce/utils/user_credentials.json

Specify the SQL database name for sales data in file: telegram_ecommerce/database/db_wrapper.py


