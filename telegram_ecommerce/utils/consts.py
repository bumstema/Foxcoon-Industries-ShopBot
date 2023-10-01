from .utils import load_json_file

default_language = "en"
currency = "CAD"
credentials_path = "telegram_ecommerce/utils/user_credentials.json"
credentials = load_json_file(credentials_path)
db_credentials = credentials["db_credentials"]
provider_token = credentials["provider_token"]
provider_live_token = credentials["provider_live_token"]
BAD_RATING = 0
REGULAR_RATING = 5
GOOD_RATING = 10


users_key = "all_users"
product_key = "all_products"
creators_key = "all_creators"
receipts_key = "all_receipts"
ui_key = "interface"
new_product_key = "new_product"
pattern_to_save_everything = "boolean_response"
