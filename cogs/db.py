import sqlite3

import cogs.config as config

conn = sqlite3.connect(config.DATABASE_NAME)

def initializeDB():
    try:
        conn.execute('''CREATE TABLE CUSTOMERS
                 (CUSTOMER_ID TEXT PRIMARY KEY NOT NULL,
                 EMAIL TEXT,
                 DISCORD_ID TEXT,
                 USER_NAME TEXT,
                 STATUS TEXT);''')
    except:
        pass

    try:
        conn.execute('''CREATE TABLE PRODUCTS
                 (PRODUCT_ID TEXT PRIMARY KEY NOT NULL,
                 NAME TEXT);''')
    except:
        pass

    try:
        conn.execute('''CREATE TABLE SUBSCRIPTIONS
                 (SUB_ID TEXT PRIMARY KEY NOT NULL,
                 CUSTOMER_ID TEXT,
                 END_PERIOD TEXT,
                 START_PERIOD TEXT,
                 PRODUCT TEXT,
                 STATUS TEXT,
                 ACTIVATION_STATUS TEXT);''')
    except:
        pass

    try:
        conn.execute('''CREATE TABLE SENT_MAIL
                 (EMAIL TEXT PRIMARY KEY NOT NULL);''')
    except:
        pass


def get_customer_id(mail):
    return conn.execute(f"SELECT CUSTOMER_ID from CUSTOMERS  where LOWER(EMAIL)='{mail.lower()}'").fetchone()[0]

def get_customer_status(mail):
    return conn.execute(f"SELECT STATUS from CUSTOMERS where LOWER(EMAIL)='{mail.lower()}'").fetchone()[0]

def get_customer_discord_id(mail):
    return conn.execute(f"SELECT DISCORD_ID from CUSTOMERS  where LOWER(EMAIL)='{mail.lower()}'").fetchone()[0]

def get_customer_id_from_discord_id(discord_id):
    return conn.execute(f"SELECT CUSTOMER_ID from CUSTOMERS  where DISCORD_ID='{discord_id}'").fetchone()[0]

def get_customers_from_discord_id(discord_id):
    return conn.execute(f"SELECT * from CUSTOMERS where DISCORD_ID='{discord_id}'")

def get_customer(mail):
    return conn.execute(f"SELECT * from CUSTOMERS where LOWER(EMAIL)='{mail.lower()}'")

def get_all_customers():
    return conn.execute(f"SELECT * from CUSTOMERS")

def get_all_linked_customers():
    return conn.execute(f"SELECT * from CUSTOMERS where DISCORD_ID!=''")

def get_product_name(product_id):
    return conn.execute(f"SELECT NAME from PRODUCTS where PRODUCT_ID='{product_id}'").fetchone()[0]

def delete_customer(mail):
    conn.execute(f"DELETE FROM CUSTOMERS where LOWER(EMAIL)='{mail.lower()}'")
    conn.commit()

def delete_subscription(customer_id):
    conn.execute(f"DELETE FROM SUBSCRIPTIONS where CUSTOMER_ID = '{customer_id}'")
    conn.commit()

def update_discord_id(discord_id, name, mail):
    conn.execute(f"UPDATE CUSTOMERS set DISCORD_ID = '{discord_id}', USER_NAME = '{name}' where LOWER(EMAIL)='{mail.lower()}'")
    conn.commit()

def update_customer_name(name, mail):
    conn.execute(f"UPDATE CUSTOMERS set USER_NAME = '{name}' where LOWER(EMAIL)='{mail.lower()}'")
    conn.commit()

def get_all_subs():
    return conn.execute(f"SELECT * from SUBSCRIPTIONS")

def get_subscription_by_customer_id(customer_id):
    return conn.execute(f"SELECT * from SUBSCRIPTIONS where CUSTOMER_ID = '{customer_id}'")

def select_customers(customer_id):
    return conn.execute(f"SELECT * from CUSTOMERS where CUSTOMER_ID = '{customer_id}'")

def update_status(sub_id, val):
    conn.execute(f"UPDATE SUBSCRIPTIONS set STATUS = '{val}' where SUB_ID = '{sub_id}'")
    conn.commit()

def update_customer_status(customer_id, val):
    conn.execute(f"UPDATE CUSTOMERS set STATUS = '{val}' where CUSTOMER_ID = '{customer_id}'")
    conn.commit()

def update_subscription(sub_id, end, activation_status):
    conn.execute(f"UPDATE SUBSCRIPTIONS set END_PERIOD = '{end}', ACTIVATION_STATUS = '{activation_status}' where SUB_ID = '{sub_id}'")
    conn.commit()

def insert_product(ids, name):
    sqlite_insert_with_param = """INSERT OR IGNORE INTO 'PRODUCTS'
            ('PRODUCT_ID', 'NAME')
            VALUES (?, ?);"""
    data_tuple = (ids, name)
    conn.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

def insert_customer(ids, email):
    sqlite_insert_with_param = """INSERT OR IGNORE INTO 'CUSTOMERS'
            ('CUSTOMER_ID', 'EMAIL', 'DISCORD_ID', 'USER_NAME', 'STATUS')
            VALUES (?, ?, ?, ?, ?);"""
    data_tuple = (ids, email, "", "", "")
    conn.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

def insert_subscription(ids, customer_id, end, start, product_name, activation_status):
    sqlite_insert_with_param = """INSERT INTO 'SUBSCRIPTIONS'
            ('SUB_ID', 'CUSTOMER_ID', 'END_PERIOD', 'START_PERIOD', 'PRODUCT', 'STATUS', 'ACTIVATION_STATUS')
            VALUES (?, ?, ?, ?, ?, ?, ?);"""
    data_tuple = (ids, customer_id, str(end), str(start), product_name, "", activation_status)
    conn.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

def insert_email(email):
    sqlite_insert_with_param = """INSERT INTO 'SENT_MAIL'
            ('EMAIL')
            VALUES (?);"""
    data_tuple = (email,)
    conn.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

def get_email_count(email):
    return conn.execute(f"SELECT COUNT(EMAIL) from SENT_MAIL  where EMAIL='{email}'").fetchone()[0]

def get_customer_count(id):
    return conn.execute(f"SELECT COUNT(CUSTOMER_ID) from SUBSCRIPTIONS  where CUSTOMER_ID='{id}'").fetchone()[0]

