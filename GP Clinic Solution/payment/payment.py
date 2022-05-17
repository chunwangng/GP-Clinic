import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
from datetime import datetime
import json
import requests
from invokes import invoke_http
import stripe

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

CORS(app)

class Payment_Logs(db.Model):
    __tablename__ = 'payment_logs'
    
    patient_phone = db.Column(db.Integer, nullable=False)
    appointment_id = db.Column(db.Integer, primary_key=True)
    payment_status = db.Column(db.String(60), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __init__(self, patient_phone, appointment_id, payment_status, price):
        self.patient_phone = patient_phone
        self.appointment_id = appointment_id
        self.payment_status = payment_status
        self.price = price
 
    def json(self):
        return {"patient_phone": self.patient_phone, "appointment_id": self.appointment_id, "payment_status": self.payment_status, "price": self.price}


payment_log_URL = "http://host.docker.internal:4242/payment_log/search/"
stripe.api_key = 'sk_test_51Ied8gJc5gcCeANGg9pMQB2ACoJVwUtYJ8ww4nwENyhTdZ86qXvgYJWk89JALZI45m53DgBxbpP7I9FI1vKHXbXY001uAwCmWs'

@app.route('/create-checkout-session/<string:patient_phone>', methods=['POST'])
def create_checkout_session(patient_phone):
  try:
    request_url = payment_log_URL + str(patient_phone) + '/unpaid'
    payment_info = requests.get(request_url, timeout=30)
    payment = payment_info.json()
    print("payment_info:", payment_info.json())
    print("payment_info:", payment_info)

    amount = str(payment['data']['Payment Logs'][0]['price'])
    amount = amount.replace('.', '')
    amount += '0' #parsing the amount to make it readable for the API receiver
    print(amount)

    session = stripe.checkout.Session.create(
      payment_method_types=['card'],
      line_items=[{
        'price_data': {
          'currency': 'sgd',
          'product_data': {
            'name': 'Medical Payment',
          },
          'unit_amount': int(amount),
        },
        'quantity': 1,
      }],
      mode='payment',
      success_url='https://google.com', #stripe_api does not allow localhost URLs, these URLs will be used to redirect the patients back to the UI when the application goes live
      cancel_url='https://google.com',
    )

    request_url = payment_log_URL + str(patient_phone) + '/unpaid'
    payment_result = requests.put(request_url, timeout=30)
    print("payment_result:", payment_result)

    return jsonify(id=session.id)

  except Exception as e:
    return jsonify({
        "message": "error occured"
    }),400


# gets all payment logs records
@app.route("/payment_log") 
def get_all():
    payment_logs = Payment_Logs.query.all()
    if len(payment_logs):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "Payment Logs": [payment_log.json() for payment_log in payment_logs]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no payment logs."
        }
    ), 404

# gets a payment log record given the appointment id
@app.route("/payment_log/<string:appointment_id>") 
def find_by_appt_id(appointment_id):
    payment_log = Payment_Logs.query.filter_by(appointment_id=appointment_id).first()
    if payment_log:
        return jsonify(

            {
                "code": 200,
                "data": payment_log.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Payment Log not found."
        }
    ), 404

#find by phonenumber
@app.route("/payment_log/search/<string:patient_phone>/<string:payment_status>", methods=['GET']) 
def find_by_phone_number(patient_phone, payment_status):
    payment_logs = Payment_Logs.query.filter_by(patient_phone=patient_phone, payment_status=payment_status).all()
    print(str(payment_logs))
    if len(payment_logs):
        return jsonify(

            {
                "code": 200,
                "data": {
                    "Payment Logs": [payment_log.json() for payment_log in payment_logs]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Payment Log not found."
        }
    ), 404


# creates a new payment log record
@app.route("/payment_log/<string:appointment_id>", methods=['POST'])
def create_payment_log(appointment_id):
    data = request.get_json()
    payment_log = Payment_Logs.query.filter_by(appointment_id=data['appointment_id']).first()
    if payment_log:
        return jsonify(
            {
                "code": 400,
                "data": {
                    "appointment_id": appointment_id
                },
                "message": "Payment Log already exists."
            }
        ), 400

    
    payment_log = Payment_Logs(**data)

    try:
        db.session.add(payment_log)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "appointment_id": appointment_id
                },
                "message": "An error occurred creating the payment log."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": payment_log.json()
        }
    ), 201

# updates a payment log record given the appointment id
# used to change total price when new prescription of same appointment is created
@app.route("/payment_log/<string:appointment_id>", methods=['PUT']) 
def update_price(appointment_id):
    data = request.get_json()
    # payment_info = Payment_Logs(**data)

    payment_log = Payment_Logs.query.filter_by(appointment_id=appointment_id).first()
    if payment_log:
        if data['payment_status']:
            payment_log.payment_status = data['payment_status']
        if data['price']:
            payment_log.price = float(data['price'])
        try:
            db.session.commit()
        except:
            return jsonify({
                "code": 400,
                "message": "An error has occured"
            })
        return jsonify(
            {
                "code": 200,
                "data": payment_log.json()
            }
        ), 200
        

# updates a payment log record given the patient phone
# used to change payment status (unpaid -> paid) after payment is made
@app.route("/payment_log/search/<string:patient_phone>/<string:payment_status>", methods=['PUT']) 
def update_payment_status(patient_phone, payment_status):
    payment_log = Payment_Logs.query.filter_by(patient_phone=patient_phone, payment_status=payment_status).first()
    if payment_log:
        payment_log.payment_status = "Paid"
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": payment_log.json()
            }
        ), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4242, debug=True)
