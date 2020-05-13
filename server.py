#! /usr/bin/env python3.6

"""
server.py
Stripe Recipe.
Python 3.6 or newer required.
"""
import sys
import traceback

import stripe
import json
import os

from flask import Flask, render_template, jsonify, request, send_from_directory
from dotenv import load_dotenv, find_dotenv

import sqlite3
from flask import current_app, g

# Setup Stripe python client library
load_dotenv(find_dotenv())
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_version = os.getenv('STRIPE_API_VERSION')

static_dir = str(os.path.abspath(os.path.join(
    __file__, "..", os.getenv("STATIC_DIR"))))
app = Flask(__name__, static_folder=static_dir,
            static_url_path="", template_folder=static_dir)
app.config['DEGUG'] = True

# Setup Database
DATABASE = 'subscription.db'


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db():
    db = g.pop('db', None)

    if db is not None:
        db.close()


def get_customer(email):
    cur = get_db().cursor()
    cur.execute("SELECT * FROM customer WHERE email=?", (email,))

    rows = cur.fetchall()

    if len(rows) == 0:
        return None
    else:
        return rows[0]


def insert_customer(email, customer_id):
    db = get_db()
    sql = ''' INSERT INTO customer(email,customer_id) VALUES(?,?) '''
    cur = db.cursor()
    cur.execute(sql, (email, customer_id))
    db.commit()
    return cur.lastrowid


@app.route('/', methods=['GET'])
def get_index():
    # print(insert_customer('webdevsmart@hotmail.com', 'customer_01'))
    # record = get_customer('webdevsmart@hotmail.com')
    # id, email, customer_id = record
    return render_template('index.html')


@app.route('/public-key', methods=['GET'])
def get_public_key():
    return jsonify(publicKey=os.getenv('STRIPE_PUBLISHABLE_KEY'))


@app.route('/create-customer', methods=['POST'])
def create_customer():
    # Reads application/json and returns a response
    data = json.loads(request.data)
    paymentMethod = data['payment_method']
    print("payment method: " + paymentMethod)

    try:
        # Check if customer already exists in db
        customer_record = get_customer(data['email'])
        if customer_record is None:
            # This creates a new Customer and attaches the PaymentMethod in one API call.
            customer = stripe.Customer.create(
                payment_method=paymentMethod,
                email=data['email'],
                invoice_settings={
                    'default_payment_method': paymentMethod
                }
            )
            # At this point, associate the ID of the Customer object with your
            # own internal representation of a customer, if you have one.
            print(customer)
            # insert customer to database
            insert_customer(data['email'], customer.id)
        else:
            customer = stripe.Customer.retrieve(customer_record[2])

        # Subscribe the user to the subscription created
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[
                {
                    "plan": os.getenv("SUBSCRIPTION_PLAN_ID"),
                },
            ],
            expand=["latest_invoice.payment_intent"]
        )

        return jsonify(subscription)
    except Exception as e:
        traceback.print_exc()
        return jsonify(error=str(e)), 403


@app.route('/subscription', methods=['POST'])
def getSubscription():
    # Reads application/json and returns a response
    data = json.loads(request.data)
    try:
        subscription = stripe.Subscription.retrieve(data['subscriptionId'])
        return jsonify(subscription)
    except Exception as e:
        return jsonify(error=str(e)), 403


@app.route('/webhook', methods=['GET', 'POST'])
def webhook_received():
    # You can use webhooks to receive information about asynchronous payment events.
    # For more about our webhook events check out https://stripe.com/docs/webhooks.
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    request_data = json.loads(request.data)

    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']

    data_object = data['object']

    if event_type == 'customer.created':
        print(data)

    if event_type == 'customer.updated':
        print(data)

    if event_type == 'invoice.upcoming':
        print(data)

    if event_type == 'invoice.created':
        print(data)

    if event_type == 'invoice.finalized':
        print(data)

    if event_type == 'invoice.payment_succeeded':
        print(data)

    if event_type == 'invoice.payment_failed':
        print(data)

    if event_type == 'customer.subscription.created':
        print(data)

    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(port=4242)
    # get_db()
    # print(insert_customer('webdevsmart@hotmail.com', 'customer_01'))
    # # insert_customer('zpedia723@hotmail.com', 'customer_02')
    # print(get_customer('webdevsmart@hotmail.com'))


def p(*args):
    print(args[0] % (len(args) > 1 and args[1:] or []))
    sys.stdout.flush()
