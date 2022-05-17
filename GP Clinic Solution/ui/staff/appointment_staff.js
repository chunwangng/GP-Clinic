function delete_button(args){
    // console.log("reading")
    document.querySelectorAll("input[name='deletebutton']")[0].addEventListener("focus", function(){
        DayPilot.Modal.confirm("Are you sure to delete this slot?", { okText: "Yes", cancelText: "No" }).then(function(e) {
            if (e.result == "OK"){
              //delete appt
              console.log(args)
              DayPilot.Http.ajax({
                url: "http://host.docker.internal:5007/appointments/delete",
                method: 'POST',
                data: {
                "appointment_id": args.e.data.id
                },
                error: function(ajax){
                  message = "An error has occured. Please try again.";
                  DayPilot.Modal.alert(message) ;
                },
                success: function(ajax){
                  message = "The appointment record was deleted.";
                  DayPilot.Modal.alert(message).then(function(args) {
                    if (args.result) {
                        args.canceled;
                        location.reload();
                    }
                }); 
                }
              })
            }
        });
          console.log(args)
        })
}

