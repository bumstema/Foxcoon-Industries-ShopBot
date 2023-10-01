
text_en = ({
    "start" : 
"""\
⭐️      Good Marfing!       ⭐️
Foxcoon Industries Shopbot
        🦊 🦝   🏭  🛒 🤖


        Let's Get Started!
            ✨ /shop ✨


/help ℹ️      /support 🌐
""",
    "help" : 

"""
===HELP===
How use this bot:
-----------------
Browse through Items for Sale: /shop
To Read the Terms of Service: /terms
For Contact Info: /support

""",
    "help_admin":
"""\n
ADMIN HELP
\n
You are Admin:
--------------
LIST OF ALL COMMANDS

1. Create category of items to sell:
/add_creator

2. Add a product to sell:
/add_product

/creator_info
/payment_info
""",
    "creator_info" :
"""==CREATOR INFO==

Contact info for hosted creators include:

""",
    "payment_info" :
"""==PAYMENT INFO==

Telegram, the company, does not collect or transmit any payment info.
Payments are processed by Stripe.

Prefered methods of payment:
 - Credit Card
 - ApplePay
 - GooglePay

A seperate checkout window should appear when ready to pay.
Sensitive information, such as credid card numbers, are not seen by the bot.

Contact /support for additional assistance.
""",
    "support" :
"""==SUPPORT==

To make a support request contact:

TELEGRAM:    @ username

EMAIL: e . mail @ email . com


Please include the following info:
[subject: TG Bot Support]
[topic: Brief description of issue]



Telegram, the company, is NOT responsible for BOTS on its platform.
Telegram or Telegram Bot Support are NOT able to help with purchases made with this BOT.
Any errors or issues (especially with transactions) must be resolved with the owners.


""",
    "terms" :
"""==TERMS AND CONDITIONS==

1️⃣ [Usage]

Users must confirm that they have read and agree to the terms and conditions before they make a purchase.
Select one of the options at the bottom of this message.

2️⃣ [Refunds]

Due to the one off nature of art commission and creation, refunds will not be given for completed materials.  \
Refunds may be given if an artwork commission has not yet begun production.  \
Discrepancies regarding creative work must be resolved with the artworks' creator(s).  \
WARNING! Commissions may be dropped or refused if creator(s) experience unnecessary harrassment by the commissioner(s).  \
The usage of this bot may be revoked for users found doing such actions.

3️⃣ [Digital Media]

Sale of strictly digital assets through Telegram are prohibited on iOS devices.  \
We advise iOS users to complete transactions of digital goods/services on other operating systesm.  \
When not available, iOS users can opt in to receive exclusive irl products such as: a real life physical handshake from the author as the service purchased with the bot, or commissions of digitally created entities (such as 'stickers') printed on a postcard.  \
For this case, please include a shipping address when checking out.

4️⃣ [Data]
Sales records are kept internally for tax purposes only.  \
Information collected from users will be limited to: name, telegram id, items purchased, date, email (if needed), shipping info (if needed).  \
Please ensure to share only the bare minimum amount of personal information needed to complete the transaction!  \
User data will not be sold to any third party companies.  \
Advertisements regarding products or services provided by the shopbot may be sent directly to users.

5️⃣ [Payment]

Payments by Credit Card is processed by Stripe, not Telegram, via secure checkout.
More info at /payment_info

6️⃣ [Support]

Bot support is NOT handled by Telegram (the company). 
More info at /support


Accept Terms to continue...
... or Reject.
""",
    "help_description" : "A long message with all commands available for you, and how to use them.",
    "start_description" : "A welcome message if you don't know this bot",
    "register_description" : "Create a password to make purchase",
    "language_description" : "Change the language.", 
    "show_categories_description" : "See products by category",
    "search_description" : "A command to search produts",
    "products_description" : "List the products available",
    "creator_info_description" : "Details to contact creators",
    "payment_info_description" : "Methods of Payment",
    "support_description" : "How to get support",
    "terms_description" : "Terms and conditions page",
    "choose_language" : "What is your language?",
    "selected_language" : "Selected language.",
    "language_dont_exist" : "The language is not supported.",
    "en" : "My language is 🇺🇸English",
    "pt" : "Minha linguagem é 🇵🇹Português",
    "cancel" : "❌Cancel",
    "previous" : "⬅️ Previous",
    "next" : "➡️ Next",
    "OK" : "👍OK",
    "price": "💳 Price: $ ",
    "rating": "The rating is: ",
    "quantity_in_stock" : "📚 In Stock: ",
    "previous_product" : "⬅️ Prev.",
    "next_product" : "Next ➡️",
    "product_details" : "⬆️ View",
    "product_cancel" : "❌ Back",
    "buy" : "⭐️ Buy",
    "ask_if_product_is_digital" : "[Yes] This a digital product.\n[No] This irlitem needs shipping.",
    "ask_if_want_create_a_password" : "Do you want to create a numeric password? (required to authenticate when making a purchase)",
    "ask_if_its_all_ok" : "Everything is alright?",
    "information_stored" : "Your information has been saved",
    "this_are_the_typed_password" : "This is the typed password. ",
    "cancelled_operation" : "Operation cancelled 🙁",
    "type_password" : "Enter your password on the numeric keypad below:",
    "user_password_has_stored" : "Your password has been stored, use it every time that you make a purchase.",
    "user_have_account" : "You already hava an account.",
    "user_dont_have_account" : "You don't have an account.  To make one, use the command /register to make an account.",
    "typing" : "You are typing: ",
    "this_is_not_a_number" : "The characters typed is not a number.",
    "this_is_not_a_integer" : "The characters typed is not a integer number.",
    "this_is_not_a_valid_type" : "Not a valid type. Choose an option from the buttons.",
    "error_when_storing_photo" : "Photo NOT stored!  Send the image as a photo instead as a file.",
    "error_when_storing_efile" : "File NOT stored!  Try again.",
    "this_is_not_a_valid_category": "This category does not exist. Use the /add_creator command to create it.",
    "ask_for_category_name" : "Enter the Name for the Creator:",
    "ask_for_category_description" : "Please Write a Creator Info Summary. Include contact details for user support.\n\nExample:\n\n'This is a bio about myself and the things I create! (etc.)\n\nTelegram @ Username \n\nEmail @ Domain . com'",
    "ask_for_category_tags" : "Type the tags of the category:",
    "ask_for_category_photo" : "Send me a photo that represents this category:",
    "ask_for_product_name" : "Type the name of the product:",
    "ask_for_product_description" : "Type the description of the product:",
    "ask_for_product_price" : "Type the price of the product:",
    "ask_for_quantity_in_stock" : "Type the number of units of this product available:",
    "ask_for_category_name_of_the_product" : "Select a creator from the list:",
    "ask_for_product_photo" : "Send me a photo which represent this product:",
    "information_dont_match" : "The database information doesn't match",
    "error_in_orders" : "An error occurred when making this order",
    "successful_payment" : "Payment has been made! Thank you!",
    "ask_if_user_want_avaluate_the_product" : "Do you want to give your opinion on this product?",
    "ask_for_the_rating" : "What is your opinion of this product?",
    "thanks_opinion" : "Thank you for your opinion! 🙂 ",
    "rating" : "User Ratings: ",
    "good" : " 👍 ",
    "bad" : " 👎 ",
    "regular" : " 😶 ",
    "stock_empty" :"The stock is empty",
    "without_product_in_this_category" : "There is no product in this category",
    "ask_for_term_to_search" : "Type to search for products:",
    "without_product_in_this_search" : "There are no products with these terms. Check for typos or search for something similar"
})
