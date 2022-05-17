<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <title>HTML5 Doctor Appointment Scheduling (JavaScript/PHP)</title>

  <link type="text/css" rel="stylesheet" href="../patient/layout.css"/>

  <!-- DayPilot library -->
  <script src="../patient/daypilot-all.min.js"></script>
  <script src="../patient/appointment.js"></script>
  <script src="appointment_staff.js"></script>
  <script src="logout.js"></script>
  <?php header("Access-Control-Allow-Origin: *"); ?>
</head>
<body>
<button type='button' value='Logout' id='Logout' onclick=logout()>Logout</button>
<div class="main">
    <div class="space">					
    </div>

  <div>

    <div class="column-left">
      <div id="nav"></div>
    </div>
    <div class="column-main">
      <div class="toolbar"><span>Available time slots:</span><button type="button" id="createnewappt">Create new appointment slots</button></div>
      
      <div id="calendar"></div>
      <div id="dp"></div>
    </div>

  </div>
</div>

<script>


 
  
  // init a calendar
  var nav = new DayPilot.Navigator("nav");
  nav.selectMode = "week";
  nav.showMonths = 3;
  nav.skipMonths = 3;
  nav.onTimeRangeSelected = function (args) {
    loadEvents(args.start.firstDayOfWeek(DayPilot.Locale.find(nav.locale).weekStarts), args.start.addDays(7));
  };
  nav.init();

  var calendar = new DayPilot.Calendar("calendar");
  calendar.viewType = "Week";
  calendar.dayBeginsHour = 9;
  calendar.dayEndsHour = 18;
  calendar.cellDuration = 5;
  calendar.timeRangeSelectedHandling = "Disabled";
  calendar.eventMoveHandling = "Disabled";
  calendar.eventResizeHandling = "Disabled";
  calendar.eventArrangement = "SideBySide";
  calendar.onBeforeEventRender = function (args) {
    if (!args.data.tags) {
      return;
    } 
    switch (args.data.tags.status) {
      case "free":
        args.data.backColor = "#4AB516";  // green
        args.data.barHidden = true;
        args.data.borderColor = "darker";
        args.data.fontColor = "white";
        args.data.html = "Available<br/>Doctor" + args.data.tags.doctor;
        args.data.toolTip = "Click to request this time slot";
        break;
      case "booked":
      args.data.backColor = "#A563CE";  // purple
      args.data.barHidden = true;
      args.data.borderColor = "darker";
      args.data.fontColor = "white";
      args.data.html = args.data.tags.patient_phone+ " has already booked this slot. <br>(Doctor "+ args.data.tags.doctor + ")";
      // console.log(args.data)
      break;
    }
  };
  document.getElementById("createnewappt").addEventListener("click", function(){
    //pop up modal to add new appt slot
    DayPilot.Http.ajax({ //get doctors list
          url: "http://host.docker.internal:5006/doctors",
          method: 'GET',
          success: function(ajax) {
            var response = ajax.data.data.doctors;
            console.log(response)
            var doctors = [];
            for (var i =0; i< response.length; i++) {
              doctors.push({name: response[i]["name"], id: response[i]["id"]})
            }
            var create_new_slots = [
              {name: "Create new appointment slot"},
              {name: "Appointment Start Day/Time", id: "appointment_start", type: "date",dateFormat : 'yyyy-MM-dd HH:mm:ss', disabled: false},
              {name: "Appointment End Day/Time", id: "appointment_end", type: "date",dateFormat : 'yyyy-MM-dd HH:mm:ss', disabled: false},
              {name: "Doctor", id: "doctor", options:doctors, disabled: false},
            ];

            DayPilot.Modal.form(create_new_slots).then(function(args) { 
              if (args.canceled) {
                return;
              }              
              DayPilot.Http.ajax({ // send to db to insert new appt slot.
                url: "http://host.docker.internal:5007/appointments/new_appointment",
                method: 'POST',
                data: {
                "appointment_start": args.result.appointment_start,
                "appointment_end": args.result.appointment_end,
                "appointment_doctor_id": args.result.doctor,
                "appointment_id": null,
                "appointment_status": null,
                "appointment_patient_phone": null
              },
                success: function(ajax) {
                  DayPilot.Modal.alert("The appointment slot has been made");
                  loadEvents();
                },
                error: function(ajax){
                  DayPilot.Modal.alert("An error has occured. Please check your entry, or you may not create an existing slot.");
                }
              })
            
              
            });

          }
    });
     
  });
  
  calendar.onEventClick = function (args) {
    if (args.e.tag("status") !== "free") { //open prescription form
      //get medication info for dropdown under prescription form
      DayPilot.Http.ajax({
          url: "http://host.docker.internal:5004/medication_info",
          method: 'GET',
          success: function(ajax) {
            var response = ajax.data.data.medications;
            // console.log(response)
            var resources = [];
            for (var i =0; i< response.length; i++) {
              resources.push({name: response[i]["med_name"], id: response[i]["med_name"]})
            }
            var prescription_form = [
              {name: "Enter prescription"},
              {name: "Appointment ID", id: "appointment_id", disabled: true},
              {name: "Medicine Name", id: "medicine_name1", options: resources , disabled: false},
              {name: "Dosage", id: "dosage1", disabled: false},
              {name: "Medicine Name", id: "medicine_name2", options: resources , disabled: false},
              {name: "Dosage", id: "dosage2", disabled: false},
              {name: "Medicine Name", id: "medicine_name3", options: resources , disabled: false},
              {name: "Dosage", id: "dosage3", disabled: false},
              {name: "", id: "deletebutton"}
            ];
            var prefilled = {
              appointment_id: args.e.data.id,
              deletebutton: "Delete this slot"
            };           
            
          var p_form = DayPilot.Modal.form(prescription_form,prefilled).then(function(args) { 
            if (args.canceled) {
              return;
            }
            
            for (var i=1; i< 4; i++){
              var med_id;
              if (args.result["medicine_name"+i]){
                if (args.result["medicine_name"+i]=='Lisinopril'){
                  med_id= '1001'
                } else if (args.result["medicine_name"+i]=='Atorvastatin'){
                  med_id= '1002'
                } else if (args.result["medicine_name"+i]=='Levothyroxine'){
                  med_id= '1003'
                } else if (args.result["medicine_name"+i]=='Metformin'){
                  med_id= '1004'
                } else if (args.result["medicine_name"+i]=='Amlodipine'){
                  med_id= '1005'
                } else if (args.result["medicine_name"+i]=='Metoprolol'){
                  med_id= '1006'
                } else if (args.result["medicine_name"+i]=='Omeprazole'){
                  med_id= '1007'
                } else if (args.result["medicine_name"+i]=='Simvastatin'){
                  med_id= '1008'
                } else if (args.result["medicine_name"+i]=='Losartan'){
                  med_id= '1009'
                } else if (args.result["medicine_name"+i]=='Clonidine'){
                  med_id= '1010'
                }
                console.log({
                "prescription_id": null, //auto increment
                "dosage": args.result["dosage"+i],
                "medicine_id": med_id,
                "appointment_id": args.result.appointment_id,
                })
                DayPilot.Http.ajax({
                url: "http://host.docker.internal:5003/prescriptions/add",
                method: 'POST',
                data: {
                "prescription_id": null, //auto increment
                "dosage": args.result["dosage"+i],
                "medicine_id": med_id,
                "appointment_id": args.result.appointment_id,
                },
                error: function(ajax){
                  message = "An error has occurred. Please try again";
                  DayPilot.Modal.alert(message) ;
                }
              })
              }            
              }
              message = "Prescription has been recorded.";
              DayPilot.Modal.alert(message);
              
          });
          delete_button(args);
          },
          error: function(ajax){ //medication info retrieval throws error
            DayPilot.Modal.alert("An error has occurred when retrieving the medication list. Please try again");
          }
        })

      
      
      return;
    }

    var form = [
      {name: "Request an Appointment"},
      {name: "From", id: "start", dateFormat: "MMMM d, yyyy h:mm tt", disabled: true},
      {name: "To", id: "end", dateFormat: "MMMM d, yyyy h:mm tt", disabled: true},
      {name: "Enter patient phone number", id:  "phone", type: "text" , disabled: false}, 
      {name: "", id: "deletebutton"}
    ];
    
    var data = {
      phone: "65",
      start: args.e.start(),
      end: args.e.end(),
      deletebutton: "Delete this slot"
    };

    var options = {
      focus: "phone"
    };

    DayPilot.Modal.form(form, data, options).then(function(modal) {
        if (modal.canceled) {
          return;
        }   
        DayPilot.Http.ajax({
          url: "http://host.docker.internal:5007/appointments/update",
          method: 'PUT',
          data: {"phone": modal.result.phone, "appointment_id": args.e.data.id},
          success: function(ajax) {
            args.e.data.tags.status = "booked";
            args.e.data.tags.patient_phone = modal.result.phone.toString().slice(2)
            calendar.events.update(args.e.data);
          }
                    
        })
        
    });
    
    delete_button(args);  
  };

  
  calendar.init();

  loadEvents();



    
    
  
</script>

</body>
</html>
