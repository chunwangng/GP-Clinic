#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import json
import os

import amqp_setup

#desktop notifications
# python -m pip install win10toast
from win10toast import ToastNotifier
import time

monitorBindingKey='*.appt_new'

# One-time initialization
toaster = ToastNotifier()

def receiveMsg():
    amqp_setup.check_setup()
    
    queue_name = "NewAppt"  

    # set up a consumer and start to wait for coming messages
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming() # an implicit loop waiting to receive messages; 
    #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nReceived a new appointment booking! Received on: " + __file__)
    processMsg(body)
    print() # print a new line feed

def processMsg(msgcontent):
    print("Printing the message details:")
    try:
        msg = json.loads(msgcontent)
        print("--JSON:", msg)
        # Show notification whenever needed
        toaster.show_toast("New appointment booking!", "Made by "+ str(msg['appointment_patient_phone'])+" for "+ str(msg['appointment_start'])+" to "+ str(msg['appointment_end'])+" for Dr. "+ str(msg['appointment_doctor_id']), threaded=True, icon_path=None, duration=7)  # 3 seconds
        while toaster.notification_active():
            time.sleep(0.1)
    except Exception as e:
        print("--NOT JSON:", e)
        print("--DATA:", msgcontent)
    print()


if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')    
    print("\nThis is " + os.path.basename(__file__), end='')
    print(": monitoring routing key '{}' in exchange '{}' ...".format(monitorBindingKey, amqp_setup.exchangename))
    receiveMsg()