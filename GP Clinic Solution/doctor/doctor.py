import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from datetime import datetime
import json
from os import environ

app = Flask(__name__)
CORS(app)  
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class Doctor(db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), nullable=False)
    
    def __init__(self, username):
        self.username = username
 
    def json(self):
        return {"name": self.username, "id":self.id}

@app.route("/doctors")
def get_all():
    doctors = Doctor.query.all()
    if len(doctors):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "doctors": [doctors.json() for doctors in doctors]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no doctors information."
        }
    ), 404

@app.route("/doctors/<string:id>")
def find_by_id(id):
    doctors = Doctor.query.filter_by(id=id).first()
    if doctors:
        return jsonify(

            {
                "code": 200,
                "data": doctors.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "doctors Info not found."
        }
    ), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)