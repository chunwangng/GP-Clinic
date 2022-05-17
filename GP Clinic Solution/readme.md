<!-- Setup instructions -->


<!-- Step 1: import all sql files under the ./sql/ folder -->
<!-- Under phpMyAdmin, login, go to User accounts and add a new user account -->
<!-- Username = is213 -->
<!-- Hostname= % -->
<!-- Password = No -->
<!-- Global privileges = SELECT, INSERT, UPDATE, DELETE, FILE -->

<!-- Step 2: docker compose -->  
<!-- Replace the docker id with your id under ./docker-compose.yml -->
<!-- In the CMD, type the following -->
cd /G7T2/
docker-compose up


<!-- Step 3: launch the notifications module -->
<!-- Open another CMD to enable pop-up notifications on Windows 10 -->
<!-- This is a feature of the AMQP implementation by the group -->
cd /G7T2/appointment/notification/
python notifcation.py

<!-- Step 4: After starting WAMP, please head to http://localhost/g7t2/ui/patient/index.html on your browser -->

<!-- Facing troubles when signing in via Patient Login? This is because your phone number must be registered
    with Twilio due to the project being a trial account. Our solution first checks if the phone number entered
    is registered with the family clinic app by checking the database.. If you have succesfully registered an account
    with us, the staff will have to manually set up your phone number with twilio to allow the number to receive SMS.
    Therefore, please leave a telegram message to @nicolsc or email peiyan.choo.2019@sis.smu.edu.sg with your phone number
    so that she can register your phone number with Twilio so that you can receive SMS on your phone. Thanks!
 -->

<!-- Features (patient) (Log out on the top right of the appointment tab)
    1. View open available slots
    2. Book any available appointment slot
    3. View Prescriptions (Their prescriptions for past medical appointments are open for viewing so that they can keep track)
    4. Make payment for a appointment (Payment amount is pre-calculated based on the prescription given)
	- Use bank card number 4242 4242 4242 4242 for a successful test transaction with Stripe (other details does not matter, could be anything)
	- Please telegram @gohweijie or email weijie.goh.2019@sis.smu.edu.sg if you require to check the successful transaction with Stripe
 -->

<!-- Or access the staff portal through http://localhost/g7t2/ui/staff/staff_login.html -->
<!-- Features (staff) (You need to log out of the patient's UI before being able to log on to the staff UI)
    1. Create appointment slots (date, time, doctor)
    2. Help a walk-in customer to book appointment (no need to pre-register with the clinic app)
    3. Delete appointment slots
    4. Key in patient prescription after consultation with the doctor for that appointment
 -->
 
<!-- To stop the services, type the following -->
docker-compose down