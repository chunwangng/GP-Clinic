window.onload = (event) => {
    var staff_id = localStorage.getItem("staff_id");
    var user_phone = localStorage.getItem("phone_number")
    setTimeout(check_credentials(staff_id, user_phone), 3000)
    // console.log(staff_id,user_phone)
   
  };

function check_credentials(staff_id, user_phone){
    setTimeout(function(){ 
      if (!user_phone && !staff_id){ //redirect user to signup page if not a staff or not logged in as patient
        window.location = 'index.html'
        console.log("no user and no staff");
    };
    var path_length = window.location.href.split("/").length 
    path_length =path_length -1
    if (window.location.href.split("/")[path_length] == "page.php"){//check if staff page
      if (staff_id){ // conditions for staff page:
        if (user_phone){ // if patient, redirect to login page.
            window.location = 'index.html'
            console.log("authorised access detected");
        };
    show_staff_page(); // if staff, show  staff pagination
    } 
       
    // console.log(user_phone)
    };
     }, 2000);
    
}

// function show_staff_page(){
//     var url_string_length = window.location.href.split("/").length;
//     var current_page_param = url_string_length -1
//     var current_page = window.location.href.split("/")[current_page_param]
//     if (current_page == "page.php") {
//         document.getElementsByClassName("space")[0].insertAdjacentHTML("beforeend","|  <a href='../patient/book_appointment.php'>Public</a><a href='page.php' style='font-weight:bold'>Staff</a>");
//     } else{
//         document.getElementsByClassName("space")[0].insertAdjacentHTML("beforeend","| <a href='index.php' style='font-weight:bold'>Public</a><a href='page.php'>Staff</a>");
//     }
// }

function loadEvents(day) { //load events in calendar
    var start = nav.visibleStart() > new DayPilot.Date() ? nav.visibleStart() : new DayPilot.Date();

    var params = {
      start: start.toString(),
      end: nav.visibleEnd().toString()
    };

    DayPilot.Http.ajax({
      url: "http://host.docker.internal:5007/appointments",
      method: 'GET',
      // data: params,
      success: function(ajax) {
        var data = ajax.data.data.appointments;
        // console.log(data);
        var appt_array= [];
        for (var i = 0 ; i < data.length; i++){
          var status = '';
          var status = data[i].appointment_status == null ? 'free' : 'booked';
          var startdateobj = new Date(data[i].appointment_start);
          startdateobj.toISOString();
          var enddateobj = new Date(data[i].appointment_end);
          enddateobj.toISOString();
          var appointment = {
            "id": data[i].appointment_id,
            "text": "",
            "start": startdateobj,
            "end": enddateobj,
            "tags": {
              "patient_phone": data[i].appointment_patient_phone,
              "status": status,
              "doctor": data[i].appointment_doctor_id
            }
          }

          appt_array.push(appointment)
        }

        if (day) {
          calendar.startDate = day;
        }
        calendar.events.list = appt_array;
        calendar.update();

        nav.events.list = data;
        nav.update();

      }
    });
  }

