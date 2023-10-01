from telegram import InputMediaPhoto

from ..language import get_text
from ..database.query import count_occurrence_of_specified_rating
from .buttons import (
    get_list_of_buttons,
    template_for_show_a_list_of_products,
    template_for_show_a_detailed_product,
                    )
from ..utils.consts import currency
from ..utils.consts import users_key, product_key, creators_key, receipts_key, ui_key, new_product_key, pattern_to_save_everything


import json

from dataclasses import dataclass, field
from ..utils.log import logger

from ..database.manipulation import  add_receipt_to_db, digital_product_was_purchased, physical_product_was_purchased, update_irl_receipt_with_buyer_info

from datetime import date, time, datetime

from ..utils.consts import *

#------------------------------------------------------------
@dataclass
class Receipt():

    transaction_id  : str = ""

    date        : str = str(datetime.now())

    creator_id  : int = 0
    buyer_id    : int = 0

    currency    : str = "CAD"
    price       : int = 0
    tip         : int = 0
    total_paid  : int = 0

    product_id  : int = 0
    successful_payment  : str = ""


    def db_values(self):
        return tuple(self.__dict__.values())

    def __repr__(self):
        return str(self.__dict__)

    def verify_irl_sale(self, user):
        if user.username not in self.transaction_id:
            return False

        if "verified" in self.successful_payment:
            return True

        self.buyer_id            = user.id
        self.successful_payment += ":verified"
        new_info = (self.transaction_id, self.buyer_id, self.successful_payment)

        update_irl_receipt_with_buyer_info(*new_info)
        return True


    def save_to_db(self):
        add_receipt_to_db(*tuple(self.__dict__.values()))
        return

    def update_sale_to_inventory(self, digital):
        if digital      :  digital_product_was_purchased(self.product_id)
        if not digital  : physical_product_was_purchased(self.product_id)
        return

#------------------------------------------------------------
@dataclass
class Sellable_Item():

    product_id  : int = 0

    name        : str = ''
    creator_id  : int = 0
    description : str = ''

    price       : int = 0
    sale_price  : int = 0

    in_stock    : int = 0
    total_sold  : int = 0

    category_id : int = 0
    image_id    : str = ''
    efile_id    : str = ''

    digital     : bool = True
    shippable   : bool = False



    def __repr__(self):
        return str(self.__dict__)

    def editable_properties(self):
        uneditable = ['product_id','creator_id','total_sold','category_id']
        editable = [item for item in list(self.__dict__.keys()) if item not in uneditable]
        return editable

    def create_a_instance_of_this_class_from_a_list_of_properties(
            properties):
        return Sellable_Item(*properties)

    def tuple_for_database(self):
        return (self.name, self.creator_id, self.description,\
            self.price, self.sale_price,\
            self.in_stock, self.total_sold,\
            self.category_id, self.image_id, self.efile_id, \
            self.digital, self.shippable )

    def sell_one(self):
        self.in_stock -= 1
        self.total_sold +=1
        
    def generate_receipt(self, checkout ):
        new_receipt             = Receipt()
        new_receipt.date        = str(datetime.now())

        new_receipt.creator_id  = self.creator_id
        new_receipt.product_id  = self.product_id

        transaction_id          = checkout['telegram_payment_charge_id']
        new_receipt.buyer_id    = int(transaction_id.split("_")[1])

        new_receipt.currency    = checkout.currency
        new_receipt.price       = self.price
        new_receipt.tip         = checkout.total_amount - self.price
        new_receipt.total_paid  = checkout.total_amount

        new_receipt.transaction_id = transaction_id
        new_receipt.successful_payment = str(checkout)
        return new_receipt

    def generate_irl_sale(self, username, amount_paid, payment_type):
        new_receipt             = Receipt()
        new_receipt.date        = str(datetime.now())

        new_receipt.creator_id  = self.creator_id
        new_receipt.product_id  = self.product_id

        transaction_id          = "token_"+new_receipt.date[0:10].replace("-","")+"_"+username+"_"+str(self.creator_id)+"_"+str(self.product_id)

        new_receipt.currency    = currency
        new_receipt.price       = self.price
        if amount_paid - self.price < 0 :
            new_receipt.tip = 0
        else:
            new_receipt.tip     = amount_paid - self.price
        new_receipt.total_paid  = amount_paid

        new_receipt.transaction_id = transaction_id
        new_receipt.successful_payment = str(payment_type)
        return new_receipt

#------------------------------------------------------------
@dataclass
class User():
    id          : int
    username    : str
    terms       : bool = False
    is_creator  : bool = False

    def __init__(self, tupes):
        self.id         = tupes[0]
        self.username   = tupes[1]
        self.terms      = not not tupes[2]
        self.is_creator = not not tupes[3]

    def __repr__(self):
        return str(self.__dict__)

#------------------------------------------------------------
@dataclass()
class Creator():
    id          : int
    username    : str
    info        : str

    def __init__(self, in_dict):
        self.__dict__.update(in_dict)

    def __repr__(self):
        return str(self.__dict__)
#------------------------------------------------------------
class Ui():
    def __init__(self):
        self.last_message = {}
        self.message_id = 0
        self.chat_id = 0

#------------------------------------------------------------
class Product():
    def __init__(self, product_id, name, description, price, quantity_in_stock,\
        quantity_purchased, category_id, image_id = None, efile_id  = None):
        self.product_id = product_id
        self.name = name
        self.description = description
        self.price = price
        self.quantity_in_stock = quantity_in_stock
        self.quantity_purchased = quantity_purchased
        self.category_id = category_id
        self.image_id = image_id
        self.efile_id = efile_id
        self.digital = True
        self.quantity_sold = 0

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return f"{self.product_id = } \n{self.name = } \n{self.description = } \n{self.price = } \n{self.quantity_in_stock = } \n{self.quantity_purchased = } \n{self.category_id = } \n{self.image_id = }  \n{self.efile_id = } "

    def create_a_instance_of_this_class_from_a_list_of_properties(
            properties):
        return Product(*properties)

#------------------------------------------------------------
#------------------------------------------------------------
class ListProductIterator():
    def __init__(self, *list_of_products):
        self.list_of_products = list_of_products
        self.iter = -1
    
    def create_a_list_from_a_query(query):
        print('create_a_list_from_a_query()')
        print(str(query))
        list_of_instances_of_Product_class = list(map(
            Sellable_Item.create_a_instance_of_this_class_from_a_list_of_properties,
            query))

        return ListProductIterator(
            *list_of_instances_of_Product_class)

    def actual(self):
        actual_product = self.list_of_products[self.iter]
        return actual_product

    def next(self):
        self.__increment_iter__()
        actual_product = self.list_of_products[self.iter]
        return actual_product

    def previous(self):
        self.__decrement_iter__()
        actual_product = self.list_of_products[self.iter]
        return actual_product

    def __increment_iter__(self):
        if self.iter == len(self.list_of_products) - 1:
            self.iter = 0
        else: 
            self.iter += 1

    def __decrement_iter__(self):
        if self.iter <= 0:
            self.iter = len(self.list_of_products) - 1
        else:
            self.iter -= 1

    def is_empty(self):
        if self.list_of_products:
            return False
        return True


#------------------------------------------------------------
def send_a_product(update, context, product, pattern_identifier):
    print('send_a_product() ')
    query = update.callback_query
    markup = template_for_show_a_list_of_products(
        pattern_identifier, context)
    text = get_text_for_product(product, context)

    print('\tchat_id = '+ str(context.chat_data[ui_key]['ui_chat_id'])+'\t'+'message_id= '+str(context.chat_data[ui_key]['ui_message_id']))
    print(str(product.image_id))
    id = context.chat_data[ui_key]['ui_chat_id']
    m_id = context.chat_data[ui_key]['ui_message_id']

    context.bot.edit_message_media( chat_id = id , message_id= m_id,\
        media = InputMediaPhoto(product.image_id, text, parse_mode='MarkdownV2'),\
        reply_markup = markup )

#------------------------------------------------------------
def send_a_detailed_product(update, context,  product, pattern_identifier):
    print('send_a_detailed_product() ')
    query = update.callback_query
    context.chat_data['current_product'] = product
    markup = template_for_show_a_detailed_product(
        pattern_identifier, update, context)
    text = get_text_for_detailed_product(product, context)

    id = context.chat_data[ui_key]['ui_chat_id']
    m_id = context.chat_data[ui_key]['ui_message_id']
    context.bot.edit_message_media( chat_id = id , message_id= m_id,\
        media = InputMediaPhoto(product.image_id, text, parse_mode='MarkdownV2'),\
        reply_markup = markup )

#------------------------------------------------------------
def get_text_for_product(product, context):
    print('get_text_for_product() ')
    text = ('*__' + markdownize(product.name) + '__*' + "\n\n"  +
        markdownize(get_text("price", context)) +' _' + markdownize( f'{product.price/100:.2f}' )+ '  '+ markdownize('('+currency+')')  + '_')
    return text

#------------------------------------------------------------
def get_text_for_detailed_product(product, context):
    logger.info('get_text_for_detailed_product() - Max text length for message: 1024')
    product_id = product.product_id
    text = '*__' + markdownize(product.name) + '__*' + "\n\n" +\
        '_' + markdownize(product.description[0:824])+'_' + '\n\n' +\
        markdownize("Price:") +' _' + markdownize( f'{product.price/100:.2f}' )+ '  '+ markdownize('('+currency+')') + '_\n\n'

    if product.digital :
        text +=  'In Stock: _Digital Item_  \t'
    if not product.digital :
        text += markdownize("In Stock: ") + '_' + markdownize(str(product.in_stock)) + '_  '
    if product.total_sold > 0:
        text += ' '+ markdownize("Sold: ") + '_' + markdownize(str(product.total_sold)) + '_'
    text +=  '\n'
    logger.info('Length of Detailed Product text: '+str(len(text)))
    #if len(text) > 1024 : text = text[0:1023]
    return (text)

#------------------------------------------------------------
def markdownize(words):
	# https://core.telegram.org/bots/api#formatting-options
	# special character list : '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!' 
    return words.replace('_','\_').replace('*','\*').replace('[','\[').replace(']','\]').replace('(','\(').replace(')','\)').replace('~','\~').replace('`','\`').replace('>','\>').replace('#','\#').replace('+','\+').replace('-','\-').replace('=','\=').replace('|','\|').replace('{','\{').replace('}','\}').replace('.','\.').replace('!','\!')
