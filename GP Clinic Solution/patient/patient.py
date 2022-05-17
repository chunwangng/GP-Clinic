import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)  
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class Patient(db.Model):
    __tablename__ = 'account'
 
    # id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(8), primary_key=True)
 
    # def __init__(self, id, name, age, phone):
    def __init__(self, name, age, phone):
        # self.id = id
        self.name = name
        self.age = age
        self.phone = phone
 
    def json(self):
        # return {"id": self.id, "name": self.name, "age": self.age, "phone": self.phone}
        return {"name": self.name, "age": self.age, "phone": self.phone}

@app.route("/patient")
def get_all():
    patients = Patient.query.all()
    if len(patients):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "patients": [patient.json() for patient in patients]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no patient information."
        }
    ), 404

@app.route("/patient/<string:phone>")
def find_by_phone(phone):
    patient = Patient.query.filter_by(phone=phone).first()
    if patient:
        return jsonify(

            {
                "code": 200,
                "data": patient.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Patient Info not found."
        }
    ), 404

@app.route("/patient/add", methods=['POST'])
def create_patient():
    data = request.get_json()
    patient_info = Patient(**data)
    # print(patient_info)
    # phone = data['phone']
    # record = Patient.query.filter_by(phone=patient_info.phone).first() #validate by phone
    # if record: 
    #     return jsonify(
    #         {
    #             "code": 400,
    #             "data": {
    #                 "id": id
    #             },
    #             "message": "Patient account already exists."
    #         }
    #     ), 400

    
    try:
        db.session.add(patient_info)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "phone": patient_info.phone
                },
                "message": "An error occurred creating the profile. Phone number already exists in the system"
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": patient_info.json()
        }
    ), 201

@app.route("/patient/delete", methods=['POST'])
def delete_book():
    data = request.get_json()
    id = data['id']
    patient = Patient.query.filter_by(id=id).first()
    if patient:
        db.session.delete(patient)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": {
                    "id": id
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "id": id
            },
            "message": "Patient info not found."
        }
    ), 404



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)