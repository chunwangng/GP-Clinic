from flask import Flask, request, jsonify # Import Flask and initialize a Flask application. We also import request and jsonify which we will need to use later.
from flask_sqlalchemy import SQLAlchemy  #Import Flask’s version of SQLAlchemy, which implicitly extends and relies on the base installation of SQLAlchemy.
from flask_cors import CORS

import os
from os import environ
## The app needs to interact with the book database to get all books, find book by isbn13 or create book.

## Instead of using raw SQL, we shall use Flask-SQLAlchemy, which is a Python SQL toolkit and Object Relational Mapper (ORM).

## ORM can be thought of as a translator that translates Python code to SQL. Hence, SQLAlchemy can be used to easily store objects into a relational database.

# from os import environ #import environ object from os

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  #disable modification tracking as it requires extra memory and is not needed.
 
db = SQLAlchemy(app) #initialize a connection to the database
 
class Staff_accounts(db.Model): # We create a new class Staff_accounts, which inherits from a basic database model, provided by SQLAlchemy. SQLAlchemy also creates a new table Book (if we run the db.create_all() function)
    __tablename__ = 'account' #specify table name as account
 
    username = db.Column(db.String(5), primary_key=True) #specify column names and params in the accounts table..
    password = db.Column(db.String(60), nullable=False)
 
    def __init__(self, username, password): #upon creation of a new row in the accounts table, we specify the properties of a accounts / define insertion rules..
        self.username = username
        self.password = password
 
    def json(self): #specify how to represent our book object as a JSON string.
        return {"username": self.username, "password": self.password}

 
@app.route("/staff_accounts/login/", methods=['POST']) 
def find_by_username():			
    data = request.get_json() 	# use get_json() to get the data from the (POST) request received. Requires the import of request in line 1.
    account = Staff_accounts(**data) 	# create a temporary instance account ** is a common idiom to allow an arbitrary number of arguments to a function, in this case, all attributes retrieved from request, instead of individually specifying each.
 
    record = Staff_accounts.query.filter_by(username=account.username, password=account.password).first()
    if record:
        return jsonify(
            {
                "code": 200,
                "data": record.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Record not found."
        }
    ), 404
 
@app.route("/staff_accounts/new_account/", methods=['POST'])	# Create new staff account 
def create_record():								# By default, entrering the URL will call line 36 as the default method is GET. If data is transmitted via POST, then this method wil be observed.
                                                        # POST request can only be satisfied through Postman or through xhr request though JS. Also possible through form submission with method POST. 
                                                        # Since we are using python, we use Postman. Project use, we used xhr request.
 
    data = request.get_json() 	# use get_json() to get the data from the (POST) request received. Requires the import of request in line 1.
    account = Staff_accounts(**data) 	# create a temporary isntance account ** is a common idiom to allow an arbitrary number of arguments to a function, in this case, all attributes retrieved from request, instead of individually specifying each.
 
    try:							# use the try-except block and return a error msg if an exception occurs when inserting a new record (row)
        db.session.add(account)		# use the db.session object (provided by SQLAlchemy) to add the book to the table and commit the changes
        db.session.commit()
    except:
        return jsonify( #fail
            {
                "code": 500,
                "message": "An error occurred creating the account. Please check if the username is less than 5 characters"
            }
        ), 500
 
    return jsonify( #success
        {
            "code": 201,
            "data": account.json() 
        })
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
