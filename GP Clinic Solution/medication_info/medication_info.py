from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from os import environ
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

class Medication_Info(db.Model):
    __tablename__ = 'medication_info'

    med_id = db.Column(db.String(4), primary_key=True)
    med_name = db.Column(db.String(20), nullable=False)
    med_price = db.Column(db.Float(precision=2), nullable=False)

    def __init__(self, med_id, med_name, med_price):
        self.med_id = med_id
        self.med_name = med_name
        self.med_price = med_price

    def json(self):
        return {"med_id": self.med_id, "med_name": self.med_name, "med_price": self.med_price}


@app.route("/medication_info")
def get_all_med_info():
    med_info_list = Medication_Info.query.all()
    if len(med_info_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "medications": [med.json() for med in med_info_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no medication information."
        }
    ), 404


@app.route("/medication_info/<string:med_id>")
def get_med_by_name(med_id):
    med = Medication_Info.query.filter_by(med_id=med_id).first()
    if med:
        return jsonify(
            {
                "code": 200,
                "data": med.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Medication not found."
        }
    ), 404

@app.route("/medication_info/add", methods=['POST'])
def create_med_info():
    data = request.get_json()
    id = data['med_id']
    try:
        med = Medication_Info.query.filter_by(med_id=id).first()
        if med:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "med_id": id,
                    },
                    "message": "Medication already exist."
                }
            ), 404
        if data['med_id']:
            name = data['med_name']
            price = data['med_price']
            new_med = Medication_Info(id, name, price)
            db.session.add(new_med)
            db.session.commit()
            return jsonify(
                {
                    "code": 201,
                    "data": new_med.json()
                }
            ), 201
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "med_id": id
                },
                "message": "An error occurred when creating medication record"
            }
        ), 500


@app.route("/medication_info/delete", methods=['POST'])
def delete_med_info():
    data = request.get_json()
    med_id = data['med_id']
    med = Medication_Info.query.filter_by(med_id=med_id).first()
    if med:
        db.session.delete(med)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": {
                    "med_id": med_id
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "med_id": med_id
            },
            "message": "Medication info not found."
        }
    ), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
