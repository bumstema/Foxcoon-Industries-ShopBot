
import mysql.connector as connector

from ..utils.utils import get_sql_commands_from_a_file
from ..utils.consts import db_credentials
from ..utils.log import logger

"""
/*
CREATE TABLE IF NOT EXISTS category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    description VARCHAR(500) NOT NULL,
    tags VARCHAR(100),
    image_id VARCHAR(150),
    FOREIGN KEY (image_id)
    REFERENCES photo (id)
) engine=MyISAM;
*/
"""

#------------------------------------------------------------
#------------------------------------------------------------
class DBWrapper():
    def __init__(self, db_credentials):
        self.database_name = "telegram_foxcoon_industries_shopbot_2023_live"
        self.connection = connector.connect(**db_credentials)
        self.connection.get_warnings = True
        if not self.this_db_exist():
            self.create_db()
            self.use_this_db()
            self.create_tables()
            print('self.create_tables()')
        else: 
            self.use_this_db()
            self.create_tables()
            print('self.use_this_db()')


    def create_db(self):
        create_db_command = (
                "CREATE DATABASE {database_name}"
                .format(database_name=self.database_name))
        self.execute_a_data_manipulation(create_db_command)


    def create_tables(self):
        create_tables_file = "telegram_ecommerce/database/create_tables.sql"
        commands = get_sql_commands_from_a_file(create_tables_file)
        cursor = self.connection.cursor()
        for command in commands:
            cursor.execute(command)
        self.connection.commit()
        cursor.close()


    def use_this_db(self):
        create_db_command = (
                "USE {database_name}"
                .format(database_name=self.database_name))
        self.execute_a_data_manipulation(create_db_command)


    def this_db_exist(self):
        database_name_tuple = (self.database_name,)
        databases_name_list = self.execute_a_query("SHOW DATABASES")
        return database_name_tuple in databases_name_list


    def execute_a_query(self, command, params=(), multi=False):
        cursor = self.connection.cursor()
        cursor.execute(command, params, multi)
        rows = cursor.fetchall()
        cursor.close()
        return rows


    def execute_a_data_manipulation(self, command, params=(), multi=False):
        cursor = self.connection.cursor()
        cursor.execute(command, params, multi)
        self.connection.commit()
        cursor.close()


    def close(self):
        self.connection.close()


#------------------------------------------------------------
db = DBWrapper(db_credentials)
logger.info("connected to database {}".format(db.database_name))

