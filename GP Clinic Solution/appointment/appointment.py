import os, sys
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from os import environ
import pika
import amqp_setup
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

CORS(app)
 
class Appointments(db.Model):
    appointment_id = db.Column(db.Integer, primary_key=True)
    appointment_start = db.Column(db.DateTime, nullable=False)
    appointment_end = db.Column(db.DateTime, nullable=False)
    appointment_status = db.Column(db.String(100), nullable=True)
    appointment_patient_phone = db.Column(db.Integer, nullable=True)
    appointment_doctor_id = db.Column(db.Integer, nullable=False)
 
    def __init__(self, appointment_id, appointment_start, appointment_end, appointment_status, appointment_patient_phone, appointment_doctor_id):
        self.appointment_id = appointment_id
        self.appointment_start = appointment_start
        self.appointment_end = appointment_end
        self.appointment_status = appointment_status
        self.appointment_patient_phone = appointment_patient_phone
        self.appointment_doctor_id = appointment_doctor_id
 
    def json(self):
        return {"appointment_id": self.appointment_id, "appointment_start": self.appointment_start, "appointment_end": self.appointment_end, "appointment_status": self.appointment_status, "appointment_patient_phone": self.appointment_patient_phone, "appointment_doctor_id": self.appointment_doctor_id}

@app.route("/appointments/")
def get_all():
    appointments = Appointments.query.all()
    if len(appointments):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "appointments": [appointment.json() for appointment in appointments]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no appointment information."
        }
    ), 404

@app.route("/appointments/update", methods=['PUT'])
def update_appointment():
    data = request.get_json()
    appt = Appointments.query.filter_by(appointment_id=data['appointment_id']).first()
    if appt:
        appt.appointment_patient_phone = data['phone'][2:]
        appt.appointment_status= 'waiting'
        try:
            db.session.commit()
        except:
            return jsonify({
                "code": 400,
                "message": "An error has occured"
            })
        sendtoexchange(appt.json())
        return jsonify(
            {
                "code": 200,
                "data": appt.json()
            }
        )

def sendtoexchange(data):
    amqp_setup.check_setup()
    message = data
    print(message)
    for key in message:
        if key == 'appointment_start':
            message[key] = message[key].strftime('%d/%m/%y %I:%M %S %p')
        if key == 'appointment_end':
            message[key] = message[key].strftime('%d/%m/%y %I:%M %S %p')
    message = json.dumps(message)
    print(message)
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="appt.appt_new", body=message, properties=pika.BasicProperties(delivery_mode = 2))
    print("\nOrder published to RabbitMQ Exchange.\n")  

@app.route("/appointments/new_appointment", methods=['POST'])
def insert_new_slot():
    data = request.get_json()
    start_time = data['appointment_start']
    doctor= data['appointment_doctor_id']
    if (Appointments.query.filter_by(appointment_start=start_time, appointment_doctor_id=doctor).first()):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "appointment_start": start_time
                },
                "message": "Appointment record already exists."
            }
        ), 400

    appointment_info = Appointments(**data)
    print(appointment_info)
    try:
        db.session.add(appointment_info)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "appointment_start": start_time
                },
                "message": "An error occurred when creating the appointment record."
            }
        ), 500
    
    return jsonify(
        {
            "code": 200,
            "data": appointment_info.json()
        }
    ), 200

@app.route("/appointments/delete", methods=['POST'])
def delete_prescription():
    data = request.get_json()
    id = data['appointment_id']
    appointment = Appointments.query.filter_by(appointment_id=id).first()
    if appointment:
        db.session.delete(appointment)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": {
                    "appointment_id": id
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "appointment_id": id
            },
            "message": "Appointment record not found."
        }
    ), 404

@app.route("/appointments/<string:appointment_patient_phone>")
def find_by_phone(appointment_patient_phone):
    appointments = Appointments.query.filter_by(appointment_patient_phone=appointment_patient_phone).all()
    if len(appointments):
        return jsonify(

            {
                "code": 200,
                "data": {
                    "appointments": [appointment.json() for appointment in appointments]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Appointment Info not found."
        }
    ), 404

@app.route("/appointments/id/<string:appointment_id>")
def find_by_id(appointment_id):
    appointments = Appointments.query.filter_by(appointment_id=appointment_id).all()
    if len(appointments):
        return jsonify(

            {
                "code": 200,
                "data": {
                    "appointments": [appointment.json() for appointment in appointments]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Appointment Info not found."
        }
    ), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=True)