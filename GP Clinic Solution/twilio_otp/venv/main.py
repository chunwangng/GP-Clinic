import os
from flask import Flask, session, request, flash, redirect, url_for, render_template
from dotenv import load_dotenv
from twilio.rest import Client
import requests

load_dotenv()
app = Flask(__name__)
app.secret_key = 'secret'
twilio_client = Client()
generateotp_url = 'https://api.generateotp.com/'


@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'GET':
        return render_template('generate.html')
    phone_number = request.form['phone_number']
    channel = request.form['channel']
    error = None
    if not phone_number:
        error = 'Phone Number is required'
    if channel != 'voice' and channel != 'sms':
        error = 'Invalid channel'
    if phone_number[0] != '+':
        error = "Please enter a valid phone number with country code, i.e. +6591234567"
    if error is None:
        # check patient db
        request_url = "http://host.docker.internal:5001/patient/" + str(phone_number[3:])
        r = requests.get(request_url, timeout=30)
        if (str(r.status_code) == "200"):
            formatted_phone_number = phone_number[1:]
            session['phone_number'] = formatted_phone_number
            otp_code = make_otp_request(formatted_phone_number)
            if otp_code:
                send_otp_code(phone_number, otp_code, channel)
                flash('Otp has been generated successfully', 'success')
                return redirect(url_for('validate'))
            else:
                error = 'Something went wrong, could not generate OTP. Please check the submitted phone number.'
                return redirect(url_for('validate'))
        else: 
            error = "Please register your phone number first before making OTP."
            flash(error, 'danger')
            return redirect(url_for('generate'))
        

@app.route('/validate', methods=['GET', 'POST'])
def validate():
    if request.method == 'GET':
        return render_template('validate.html')
    otp_code = request.form['otp_code']
    error = None
    if not otp_code:
        error = 'Otp code is required'
    if 'phone_number' in session:
        phone_number = session['phone_number']
    else:
       error = 'Please request for a new OTP'
    if error is None:
        session.pop('phone_number', None)
        status, message = verify_otp_code(otp_code, phone_number)
        if status == True:
           flash(message, 'success')
           redirect_url = 'http://localhost/g7t2/ui/patient/book_appointment.php'
           wait_time = 3000
           seconds = wait_time / 1000
           # if the validation is successful, forward to redirect page, wait 3 seconds, redirect to specified url
           return f"<html><body><p>Sucessful authentication. You will be redirected in { seconds } seconds</p><form action='{redirect_url}' method='POST' id='success'><input type='hidden' id='phone_number' name='phone_number'></form><script>window.onload = (event) => {{document.querySelectorAll('input[id=\"phone_number\"]')[0].value = {phone_number};setTimeout(document.getElementById('success').submit(), 3000)}}</script></body></html>"           #put session in this html above.
        if status == False:
           flash(message, 'danger')
           return redirect(url_for('validate'))
        error = 'Something went wrong, could not validate OTP'
    flash(error, 'danger')
    return redirect(url_for('generate'))

def verify_otp_code(otp_code, phone_number):
    r = requests.post(f"{generateotp_url}/validate/{otp_code}/{phone_number}")
    if r.status_code == 200:
        data = r.json()
        status = data["status"]
        message = data["message"]
        return status, message
    return None, None


def make_otp_request(phone_number):
    r = requests.post(f"{generateotp_url}/generate",
                      data={'initiator_id': phone_number})
    if r.status_code == 201:
        data = r.json()
        otp_code = str(data["code"])
        return otp_code


def send_otp_code(phone_number, otp_code, channel):
    if channel == 'voice':
        return send_otp_via_voice_call(phone_number, otp_code)
    if channel == 'sms':
        return send_otp_via_sms(phone_number, otp_code)


def send_otp_via_voice_call(number, code):
    outline_code = split_code(code)
    call = twilio_client.calls.create(
        twiml=f"<Response><Say voice='alice'>Your one time password is {outline_code}</Say><Pause length='1'/><Say>Your one time password is {outline_code}</Say><Pause length='1'/><Say>Goodbye</Say></Response>",
        to=f"{number}",
        from_=os.getenv('TWILIO_NUMBER')
    )


def send_otp_via_sms(number, code):
    messages = twilio_client.messages.create(to=f"{number}", from_=os.getenv(
        'TWILIO_NUMBER'), body=f"Your one time password is {code}")


def split_code(code):
    return " ".join(code)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=7000, debug=True)