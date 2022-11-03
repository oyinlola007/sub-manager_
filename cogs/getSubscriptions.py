import requests, json, sqlite3
from datetime import datetime

import cogs.config as config
import cogs.strings as strings
import cogs.db as db

def get_products():
    ids = ""
    while True:
        if ids == "":
            r = requests.get(config.PRODUCTS_URL1.format(config.LIMIT), headers=config.HEADERS)
        else:
            r = requests.get(config.PRODUCTS_URL2.format(config.LIMIT, ids), headers=config.HEADERS)
        data = json.loads(r.text)

        products = data["data"]
        if len(products) == 0:
            ids = ""
            break

        for product in products:
            try:
                ids = product["id"]
                name = product["name"]
                db.insert_product(ids, name)
            except:
                pass

def get_customers():
    ids = ""
    while True:
        if ids == "":
            r = requests.get(config.CUSTOMERS_URL1.format(config.LIMIT), headers=config.HEADERS)
        else:
            r = requests.get(config.CUSTOMERS_URL2.format(config.LIMIT, ids), headers=config.HEADERS)
        data = json.loads(r.text)

        customers = data["data"]
        if len(customers) == 0:
            ids = ""
            break

        for customer in customers:
            try:
                ids = customer["id"]
                email = customer["email"]
                db.insert_customer(ids, email)
            except:
                pass

def get_subscriptions():
    ids = ""
    while True:
        if ids == "":
            r = requests.get(config.SUBSCRIPTIONS_URL1.format(config.LIMIT), headers=config.HEADERS)
        else:
            r = requests.get(config.SUBSCRIPTIONS_URL2.format(config.LIMIT, ids), headers=config.HEADERS)
        data = json.loads(r.text)

        subscriptions = data["data"]
        if len(subscriptions) == 0:
            ids = ""
            break

        for subscription in subscriptions:
            try:
                ids = subscription["id"]
                customer_id = subscription["customer"]
                end = subscription["current_period_end"]
                start = subscription["current_period_start"]
                product = subscription["plan"]["product"]
                activation_status = subscription["status"]

                product_name = db.get_product_name(product)
                db.insert_subscription(ids, customer_id, end, start, product_name, activation_status)
            except:
                db.update_subscription(ids, end, activation_status)
