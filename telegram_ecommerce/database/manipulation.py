from .db_wrapper import db
from .query import (
    user_in_credentials_file, 
    get_quantity_in_stock,
    get_quantity_purchased)

from ..utils.log import logger

#------------------------------------------------------------
#  USER
#------------------------------------------------------------
def create_account(user):
    user_id         = user.id
    username        = user.username
    user_terms      = user.terms
    user_is_creator = user_in_credentials_file(username)
    #command = "UPDATE customers SET password_hash = %s WHERE id = %s"
    command = ("""
        INSERT INTO customers 
            (id, username, terms, is_creator)
            VALUES (%s, %s, %s, %s)""")
    command_args = (user_id, username, user_terms, user_is_creator)
    db.execute_a_data_manipulation(command, command_args)

#------------------------------------------------------------
def delete_account(user_id):
    command = "DELETE FROM customers WHERE id = %s"
    db.execute_a_data_manipulation(command, (user_id,))

#------------------------------------------------------------
def set_terms_true(user_id):
    command = "UPDATE customers SET terms = %s WHERE id = %s"
    db.execute_a_data_manipulation(command, (True, user_id))
    
#------------------------------------------------------------


#------------------------------------------------------------
#  CREATOR CATEGORY
#------------------------------------------------------------
def add_category(name, telegram_id, description):
    logger.info('Adding Creator to sql db.')
    command = (""" INSERT INTO category
            (name,
            creator_id,
            description)
        VALUES (%s, %s,  %s)""")
    command_args = (name, telegram_id, description)
    db.execute_a_data_manipulation(command, command_args)

#------------------------------------------------------------
def delete_category_from_db(name):
    command = "DELETE FROM category WHERE name = %s"
    db.execute_a_data_manipulation(command, (name,))

#------------------------------------------------------------
def update_category_description(telegram_id, description):
    logger.info('Updating Creator Description in sql db.')
    command = ("""UPDATE category SET description = %s WHERE creator_id = %s""")
    command_args = (description, telegram_id)
    db.execute_a_data_manipulation(command, command_args)
    return

#------------------------------------------------------------
#  PRODUCTS
#------------------------------------------------------------
def add_product(
    name,
    creator_id,
    description,
    price=0,
    sale_price=0,
    in_stock=0,
    total_sold=0,
    category_id=None, 
    image_id=None,
    efile_id=None,
    digital=True,
    shippable=False):
    command = ("""
        INSERT INTO products
            (name, 
            creator_id,
            description,
            price, 
            sale_price,
            in_stock,
            total_sold,
            category_id, 
            image_id,
            efile_id,
            digital,
            shippable)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""")
    command_args = (
        name,
        creator_id,
        description,
        int(price),
        int(sale_price),
        int(in_stock),
        int(total_sold),
        int(category_id), 
        image_id,
        efile_id,
        digital,
        shippable)
    print('command  :  ' + str(command))
    print('command_args  :  ' + str(command_args))
    db.execute_a_data_manipulation(command, command_args)

#------------------------------------------------------------
def update_product(item_property, item_value, product_id):
    command = f"UPDATE products SET {item_property} = %s WHERE id = %s"
    db.execute_a_data_manipulation(command, (item_value, product_id))

#------------------------------------------------------------
def delete_product_from_db(name):
    command = "DELETE FROM products WHERE name = %s"
    db.execute_a_data_manipulation(command, (name,))

#------------------------------------------------------------
def delete_product_from_db_by(value):
    logger.info(f'{property} {value}')
    command = "DELETE FROM products WHERE name = %s"
    db.execute_a_data_manipulation(command, (value,))

#------------------------------------------------------------
def digital_product_was_purchased(product_id):
    total_sold = get_quantity_purchased(product_id) + 1
    command = ("""
        UPDATE products SET total_sold = %s WHERE id = %s""")
    command_args = (total_sold, product_id)
    db.execute_a_data_manipulation(command, command_args)

#------------------------------------------------------------
def physical_product_was_purchased(product_id):
    in_stock = get_quantity_in_stock(product_id) - 1
    total_sold = get_quantity_purchased(product_id) + 1
    command = ("""
        UPDATE products SET  in_stock = %s, total_sold = %s WHERE id = %s""")
    command_args = (in_stock, total_sold, product_id)
    db.execute_a_data_manipulation(command, command_args)

#------------------------------------------------------------
#  PHOTO
#------------------------------------------------------------
def update_photo(photo_id, blob):
    command = "UPDATE photo SET image_blob = %s WHERE id = %s"
    command_args = (bytes(blob), photo_id)
    db.execute_a_data_manipulation(command, command_args)

#------------------------------------------------------------
def add_photo(photo_id, bytes_of_photo):
    command = "INSERT INTO photo (id) VALUES (%s)"
    command_args = (photo_id,)
    db.execute_a_data_manipulation(command, command_args)
    update_photo(photo_id, bytes_of_photo)

#------------------------------------------------------------
#  EFILES
#------------------------------------------------------------
def update_eflie(efile_id, blob):
    command = "UPDATE efiles SET efile_blob = %s WHERE id = %s"
    command_args = (bytes(blob), efile_id)
    db.execute_a_data_manipulation(command, command_args)

#------------------------------------------------------------
def add_efile(efile_id, bytes_of_efile):
    command = "INSERT INTO efiles (id) VALUES (%s)"
    command_args = (efile_id,)
    db.execute_a_data_manipulation(command, command_args)
    update_photo(efile_id, bytes_of_efile)

#------------------------------------------------------------
#  RECEIPTS
#------------------------------------------------------------
def add_receipt_to_db(
    transaction_id,
    date, creator_id, buyer_id, \
    currency, price, tip, total_paid, \
    product_id, successful_payment):
    logger.info('Adding Receipt to DB.')
    command = ("""INSERT INTO receipts
        (transaction_id, date, creator_id, buyer_id, currency, price, tip, total_paid, product_id, successful_payment )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""")
    command_args = (
        transaction_id,
        date,
        int(creator_id),
        int(buyer_id),
        currency,
        int(price),
        int(tip),
        int(total_paid),
        int(product_id),
        successful_payment)
    db.execute_a_data_manipulation(command, command_args)

#------------------------------------------------------------
def update_irl_receipt_with_buyer_info(transaction_id, buyer_id, successful_payment):
    logger.info('Adding Buyer Info to DB.')
    command = ("""
        UPDATE receipts SET buyer_id = %s, successful_payment = %s WHERE transaction_id = %s""")
    command_args = (buyer_id, successful_payment, transaction_id)
    db.execute_a_data_manipulation(command, command_args)

##
#REMOVE RATINGS
#------------------------------------------------------------
def add_rating_to_an_order(order_id, rating):
    command = ("""
        UPDATE orders SET
            rating = %s
        WHERE id = %s""")
    command_args = (int(rating), order_id)
    db.execute_a_data_manipulation(command, command_args)
