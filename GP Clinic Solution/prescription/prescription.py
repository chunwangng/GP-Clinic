import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_cors import CORS
from os import environ
from datetime import datetime
import json
from invokes import invoke_http
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

CORS(app)

class Prescriptions(db.Model):
    __tablename__ = 'prescriptions'
    
    prescription_id = db.Column(db.Integer, primary_key=True)
    dosage = db.Column(db.String, nullable=False)
    medicine_id = db.Column(db.Integer, nullable=False)
    appointment_id = db.Column(db.Integer, nullable=False)
 
    def __init__(self, prescription_id, dosage, medicine_id, appointment_id):
        self.prescription_id = prescription_id
        self.dosage = dosage
        self.medicine_id = medicine_id
        self.appointment_id = appointment_id
 
    def json(self):
        return {"prescription_id": self.prescription_id, "dosage": self.dosage, "medicine_id": self.medicine_id, "appointment_id": self.appointment_id}

@app.route("/prescriptions")
def get_all():
    prescriptions_list = Prescriptions.query.all()
    if len(prescriptions_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "prescriptions": [prescription.json() for prescription in prescriptions_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no prescription records."
        }
    ), 404

@app.route("/prescriptions/<string:appointment_id>")
def find_by_appointment_id(appointment_id):
    prescriptions = Prescriptions.query.filter_by(appointment_id=appointment_id)
    if prescriptions:
        return jsonify(

            {
                "code": 200,
                "data": [prescription.json() for prescription in prescriptions]
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no prescriptions found for this appointment ID."
        }
    ), 404


@app.route("/prescriptions/add", methods=['POST'])
def create_prescription():
    data = request.get_json()
    prescription_info = Prescriptions(**data)
    try:
        db.session.add(prescription_info)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred when creating the prescription record."
            }
        ), 500
       
    return processNewPrescription(prescription_info.json())
    # return jsonify(
    #     {
    #         "code": 200,
    #         "data": prescription_info.json()
    #     }, 
    # ), 200

def processNewPrescription(prescription_details):

    appointment_URL = "http://host.docker.internal:5007/appointments/id/"
    medication_info_URL = "http://host.docker.internal:5004/medication_info/"
    payment_log_URL = "http://host.docker.internal:4242/payment_log/"

    print(prescription_details)
    medicine_id = prescription_details["medicine_id"]
    appointment_id = prescription_details["appointment_id"]

    # Retrieve patient phone number from appointment microservice
    print("\n-----Invoking appointment microservice-----")
    request_url = appointment_URL + str(appointment_id)
    appointment_response = requests.get(request_url, timeout=30)
    appointment_result = appointment_response.json()

    # patient_phone = 0
    
    for a in appointment_result:
        if a == 'data':
            for b in appointment_result[a]:
                if b == 'appointments':
                    for c in appointment_result[a][b]:
                        patient_phone = str(c['appointment_patient_phone'])

    # Create new payment log
    # Invoke medication info microservice
    print("\n-----Invoking medication info microservice-----")
    price = 0
    request_url = medication_info_URL + str(medicine_id)
    medication_info_response = requests.get(request_url, timeout=30)
    medication_info_result = medication_info_response.json()
    for a in medication_info_result:
        if a == 'data':
            for b in medication_info_result[a]:
                if b == 'med_price':
                    price = str(medication_info_result[a][b])
    
    # check if appointment exist in payment log using appt id
    # invoke payment log microservice
    print("\n-----Invoking payment log microservice-----")
    request_url = payment_log_URL + str(appointment_id)
    payment_log_response = requests.get(request_url, timeout=30)
    payment_log_check_result = payment_log_response.json()
    code = payment_log_check_result["code"]
    print(payment_log_check_result)

    # if code == 200: payment log already exist, appointment has more than 1 prescription. Invoke payment log microservice and update payment log.
    if code == 200:
        old_price = payment_log_check_result["data"]["price"]
        print(old_price)
        new_price = 0
        new_price = float(old_price) + float(price)
        print(new_price)

        print("\n-----Invoking payment log microservice-----")
        updated_log = {
            "payment_status": "Unpaid",
            "price": new_price
        }
        request_url = payment_log_URL + str(appointment_id)
        headers = {"content-type": "application/json" }
        payment_log_update = requests.put(request_url, data=json.dumps(updated_log), headers=headers, timeout=30)
        payment_log_update_result = payment_log_update.json()
        # return str(payment_log_update_result)
        print(payment_log_update_result)
        return jsonify({
            "code": 200,
            "data": {
                "payment_log_create": payment_log_update_result
            }
        })

    # if code == 404: payment log dont exist. Appointment's first prescription. Create new payment log.
    elif code == 404:
        print("\n-----Invoking payment log microservice-----")
        new_log = {
            "appointment_id": appointment_id,
            "patient_phone": patient_phone,
            "payment_status": "Unpaid",
            "price": price
        }
        request_url = payment_log_URL + str(appointment_id)
        headers = {"content-type": "application/json" }
        payment_log_create_response = requests.post(request_url, data=json.dumps(new_log), headers=headers,timeout=30)
        payment_log_create_result = payment_log_create_response.json()
        print(payment_log_create_result)
        # return str(payment_log_create_result)
        return jsonify({
            "code": 200,
            "data": {
                "payment_log_create": payment_log_create_result
            }
        })

@app.route("/prescriptions/delete", methods=['POST'])
def delete_prescription():
    data = request.get_json()
    id = data['prescription_id']
    prescription = Prescriptions.query.filter_by(prescription_id=id).first()
    if prescription:
        db.session.delete(prescription)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": {
                    "prescription_id": id
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "prescription_id": id
            },
            "message": "Prescription record not found."
        }
    ), 404


@app.route("/medication_history/<string:patient_id>")
def get_medication_history(patient_id):
    patient_URL = "http://host.docker.internal:5001/patient/"
    appointment_URL = "http://host.docker.internal:5007/appointments/"
    medicine_URL = "http://host.docker.internal:5004/medication_info"
    try:
        print("\n-----Invoking patient microservice-----")
        request_url = patient_URL + str(patient_id)
        patient_result = requests.get(request_url, timeout=30)

        print("\n-----Invoking appointment microservice-----")
        request_url = appointment_URL + str(patient_id)
        appointment_result = requests.get(request_url, timeout=30)
        
        print("\n-----Invoking medicine information microservice-----")
        request_url = medicine_URL 
        medicine_info = requests.get(request_url, timeout=30)

        return {
            "code": 200,
            "data": {
                "patient_result": patient_result.json(),
                "appointment_result": appointment_result.json(),
                "medicine_info": medicine_info.json()
            },
        }
    except Exception as e:
        return jsonify({
            "message": "error occured"
        }),500

# @app.route("/newPrescription", methods=["POST"])
# def makeNewPrescription():
#     # Simple check of input format and data of the request are JSON
#     if request.is_json:
#         try:
#             prescription_details = request.get_json()
#             print("\nReceived an order in JSON:", prescription_details)

#             # do the actual work
#             # 1. Send prescription details
#             result = processNewPrescription(prescription_details)
#             return jsonify(result), result["code"]

#         except Exception as e:
#             pass  # do nothing.

#     # if reached here, not a JSON request.
#     return jsonify({
#         "code": 400,
#         "message": "Invalid JSON input: " + str(request.get_data())
#     }), 400



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)