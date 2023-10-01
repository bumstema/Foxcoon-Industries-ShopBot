from .db_wrapper import db
from ..utils.consts import credentials
from ..utils.utils import (
    write_file,
    extract_value_from_a_query,
    extract_list_of_values_from_a_query,
    hash_password)
from ..utils.log import logger

#------------------------------------------------------------
#  QUERY - USERS  (customers)
#------------------------------------------------------------
def user_exist(user_id):
    print('user_exist()')
    command = "SELECT * FROM customers WHERE id = %s"
    user_exist = bool(db.execute_a_query(command, (user_id,)))
    return user_exist

#------------------------------------------------------------
def user_in_credentials_file(username):
    print('user_in_credentials_file()')
    admins = credentials["admins_username"]
    return username in admins

#------------------------------------------------------------
def is_admin(user_id):
    print('is_admin()')
    command = "SELECT is_admin FROM customers WHERE id = %s"
    user_is_admin = db.execute_a_query(command, (user_id,))
    user_exist = bool(user_is_admin)
    if user_exist:
        return extract_value_from_a_query(user_is_admin)
    else: return False

#------------------------------------------------------------
def get_all_available_by_user_id(user_id):
    print('get_all_available_by_user_id()')
    command = """ SELECT * FROM customers
        WHERE id = %s """
    user_with_id = db.execute_a_query(
        command, (user_id,))
    return user_with_id

#------------------------------------------------------------
def username_from_user_id(user_id):
    print('username_from_user_id()')
    command = "SELECT username FROM customers WHERE id = %s"
    user_name = db.execute_a_query(command, (user_id,))
    return extract_value_from_a_query(user_name)


#------------------------------------------------------------
#  QUERY - PHOTO
#------------------------------------------------------------
def extract_blob(photo_id):
    print('extract_blob()')
    command = "SELECT image_blob FROM photo WHERE id = %s"
    blob = bytes(
        extract_value_from_a_query(
        db.execute_a_query(command, (photo_id,)))
        )
    return blob

#------------------------------------------------------------
def save_photo_in_file(photo_id, file_path):
    print('save_photo_in_file()')
    blob = extract_blob(photo_id)
    write_file(blob, file_path)


#------------------------------------------------------------
#  QUERY - EFILE
#------------------------------------------------------------
def extract_efile_blob(efile_id):
    print('extract_efile_blob()')
    command = "SELECT efile_blob FROM efile WHERE id = %s"
    blob = bytes(
        extract_value_from_a_query(
        db.execute_a_query(command, (efile_id,)))
        )
    return blob

#------------------------------------------------------------
def save_efile_in_file(efile_id, file_path):
    print('save_efile_in_file()')
    blob = extract_blob(efile_id)
    write_file(blob, file_path)


#------------------------------------------------------------
#  QUERY - CATEGORY    (CREATORS)
#------------------------------------------------------------
def get_name_of_all_categories():
    print('get_name_of_all_categories()')
    command = "SELECT name FROM category"
    all_names_query = db.execute_a_query(command)
    names = extract_list_of_values_from_a_query(all_names_query)
    return names 

#------------------------------------------------------------
def get_category_id_from_name(name):
    print('get_category_id_from_name()')
    command = "SELECT id FROM category WHERE name = %s"
    category_id = db.execute_a_query(command, (name,))
    return extract_value_from_a_query(category_id)

#------------------------------------------------------------
def get_category_id_from_creator_id(creator_id):
    print('get_category_id_from_creator_id()')
    command = "SELECT id FROM category WHERE creator_id = %s"
    category_id = db.execute_a_query(command, (creator_id,))
    return extract_value_from_a_query(category_id)

#------------------------------------------------------------
def get_all_descriptions_from_all_creators():
    print('get_all_descriptions_from_all_creators()')
    command = """ SELECT description FROM category
        WHERE id > %s """
    descriptions_from_creators = db.execute_a_query(
        command, (0,))
    return descriptions_from_creators

#------------------------------------------------------------
def get_description_from_creator_id(creator_id):
    print('get_description_from_creator_id()')
    command = """ SELECT description FROM category
        WHERE creator_id = %s """
    creator_description = db.execute_a_query(
        command, (creator_id,))
    return extract_value_from_a_query(creator_description)

#------------------------------------------------------------
def get_all_available_by_category_name(name):
    print('get_all_available_by_category_name()')
    category_id = get_category_id_from_name(name)
    return get_all_available_by_category_id(category_id)


#------------------------------------------------------------
#  QUERY - PRODUCTS
#------------------------------------------------------------
def get_quantity_purchased(product_id):
    print('get_quantity_purchased()')
    command = "SELECT total_sold FROM products WHERE id = %s"
    quantity_purchased = db.execute_a_query(command, (product_id,))
    return extract_value_from_a_query(quantity_purchased)

#------------------------------------------------------------
def get_quantity_in_stock(product_id):
    print('get_quantity_in_stock()')
    command = "SELECT in_stock FROM products WHERE id = %s"
    quantity_in_stock = db.execute_a_query(command, (product_id,))
    return extract_value_from_a_query(quantity_in_stock)


#------------------------------------------------------------
def get_efile_id_from_product_id(product_id):
    print('get_efile_id_from_product_id()')
    command = """ SELECT efile_id FROM products WHERE id = %s """
    efile_id_from_db = db.execute_a_query(
        command, (product_id,))
    return extract_value_from_a_query(efile_id_from_db)

#------------------------------------------------------------
def get_all_available_by_category_id(category_id):
    print('get_all_available_by_category_id()')
    command = """ SELECT * FROM products 
        WHERE category_id = %s AND in_stock > 0"""
    products_with_category_id = db.execute_a_query(
        command, (category_id,))
    return products_with_category_id


#------------------------------------------------------------
#  QUERY - RECEIPTS
#------------------------------------------------------------

def customers_names_from_receipts_by_product_id(product_id):

    command = ("""
        SELECT buyer_id FROM receipts WHERE product_id = %s""")
    command_args = (product_id,)
    ids_query = db.execute_a_query(command,  command_args)
    return extract_list_of_values_from_a_query(ids_query)

##
# REMOVE RATINGS
#------------------------------------------------------------
def get_ratings_of_a_product(product_id):
    print('get_ratings_of_a_product()')
    command = """ SELECT rating FROM orders
        WHERE product_id = %s AND rating IS NOT NULL"""
    ratings_query = db.execute_a_query(command, (product_id,))
    return extract_list_of_values_from_a_query(ratings_query)

#------------------------------------------------------------
def count_occurrence_of_specified_rating(product_id, rating):
    print('count_occurrence_of_specified_rating()')
    all_ratings = get_ratings_of_a_product(product_id)
    return all_ratings.count(rating)

#------------------------------------------------------------
def search_products(string_to_search):
    print('search_products()')
    command = """SELECT * FROM products 
        WHERE MATCH(name, description) AGAINST(%s)"""
    products_that_match = (
        db.execute_a_query(command, (string_to_search,)))
    return products_that_match 
