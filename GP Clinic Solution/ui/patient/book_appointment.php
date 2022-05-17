<!doctype html>
<html lang="en">

<head>
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
	<meta name="viewport" content="width=device-width">
	<title>Patient</title>
	<link rel="canonical" href="https://getbootstrap.com/docs/5.0/examples/dashboard/">
	<!--[if lt IE 9]>
	<script src="//html5shiv.googlecode.com/svn/trunk/html5.js"></script>
	<![endif]-->
	<!-- Bootstrap libraries -->
	<meta name="viewport" 
		content="width=device-width, initial-scale=1, shrink-to-fit=no">
	<!-- Latest compiled and minified CSS -->
	<link rel="stylesheet"
		href="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css"
		integrity="sha384-GJzZqFGwb1QTTN6wy59ffF1BuGJpLSa9DkKMp0DgiMDm4iYMj70gZWKYbI706tWS" 
		crossorigin="anonymous">
	<!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
	<script 
		src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
	<script
		src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.6/umd/popper.min.js"
		integrity="sha384-wHAiFfRlMFy6i5SRaxvfOCifBUQy1xHdJ/yoi7FRNXMRBu5WHdZYu1hA6ZOblgut"
		crossorigin="anonymous"></script>
	<script 
		src="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/js/bootstrap.min.js"
		integrity="sha384-B0UglyR+jN6CkvvICOB2joaf5I4l3gm9GU6Hc1og6Ls7i6U/mkkaduKaBhlAXv9k"
		crossorigin="anonymous"></script>
	<!-- UI style -->
	<link type="text/css" rel="stylesheet" href="style.css"/>
    <!-- <script src="../dashboard.js"></script> -->
    <link href="dashboard.css" rel="stylesheet">

	<!-- DayPilot library -->
	<script src="daypilot-all.min.js"></script>
	<script src="appointment.js"></script>

	<script src="logout.js"></script>
</head>
  
<body>
	<header class="navbar navbar-dark sticky-top bg-dark flex-md-nowrap p-0 shadow">
	<a class="navbar-brand" href="#">Family Clinic</a>
	<button class="navbar-toggler position-absolute d-md-none collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#sidebarMenu" aria-controls="sidebarMenu" aria-expanded="false" aria-label="Toggle navigation">
		<span class="navbar-toggler-icon"></span>
	</button>
	<ul class="navbar-nav px-3">
		<li class="nav-item text-nowrap">
		<button type='button' value='Logout' id='Logout' onclick=logout()>Logout</button>
		</li>
	</ul>
	</header>
	<div class="container-fluid d-flex">
		<div class="row" id="sidediv">
			<nav id="sidebarMenu" class="d-md-block bg-light sidebar collapse">
				<div class="position-sticky pt-3">
					<ul class="nav flex-column">
						<li class="nav-item">
							<a class="nav-link active" href="book_appointment.php">
							<span data-feather="bookmark"></span>
							Book Appointment
							</a>
						</li>
						<li class="nav-item">
							<a class="nav-link" href="view_prescriptions.html">
							<span data-feather="eye"></span>
							View Prescriptions
							</a>
						</li>
						<li class="nav-item">
							<a class="nav-link" href="make_payments.html">
							<span data-feather="dollar-sign"></span>
							Make Payment
							</a>
						</li>
					</ul>
				</div>
			</nav>
		</div>
		<div class="maindiv" id="main" style="display:inline-block;width: 100%;">
			<?php 
				if (isset($_POST['phone_number'])){ //set phone number in session for first time after user comes to this page
				  $_SESSION['phone_number'] = $_POST['phone_number'] ;
				  echo '<script> localStorage.setItem("phone_number", "' . $_SESSION['phone_number']  . '");</script>';
				  $_POST = array();
				}
			?>
			<div class="main">
				<div class="space">					
				</div>
				<div style="display:flex">
					<div class="column-left">
						<div id="nav"></div>
					</div>
					<div class="column-main" style="width:100%; padding: 0 1%">
						<div class="toolbar">Available time slots:</div>
						<div id="calendar"></div>
					</div>
				</div>
			</div>
			<!-- end -->
		</div>
	</div>
	<!-- <script src="../assets/dist/js/bootstrap.bundle.min.js"></script> -->
	<script src="https://cdn.jsdelivr.net/npm/feather-icons@4.28.0/dist/feather.min.js" integrity="sha384-uO3SXW5IuS1ZpFPKugNNWqTZRRglnUJK6UAZ/gxOX80nxEkN9NcGZTftn6RzhGWE" crossorigin="anonymous"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@2.9.4/dist/Chart.min.js" integrity="sha384-zNy6FEbO50N+Cg5wap8IKA4M/ZnLJgzc6w2NqACZaK0u0FXfOWRRJOnQtpZun8ha" crossorigin="anonymous"></script>
	<script>
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
		    case "waiting":
		      args.data.backColor = "#e69138";  // orange
		      args.data.barHidden = true;
		      args.data.borderColor = "darker";
		      args.data.fontColor = "white";
		      args.data.html = "Your appointment, waiting for confirmation";
		      break;
		    case "confirmed":
		      args.data.backColor = "#3D85C6";  // blue
		      args.data.barHidden = true;
		      args.data.borderColor = "darker";
		      args.data.fontColor = "white";
		      args.data.html = "Your appointment, confirmed";
		      break;
		    case "booked":
		    args.data.backColor = "#A563CE";  // purple
		    args.data.barHidden = true;
		    args.data.borderColor = "darker";
		    args.data.fontColor = "white";
		    args.data.html = "Someone has already booked this slot";
		    break;
		  }
		};
		calendar.onEventClick = function (args) {
		  if (args.e.tag("status") !== "free") {
		    calendar.message("You can only request a new appointment in a free slot.");
		    return;
		  }
		
		  var form = [
		    {name: "Request an Appointment"},
		    {name: "From", id: "start", dateFormat: "MMMM d, yyyy h:mm tt", disabled: true},
		    {name: "To", id: "end", dateFormat: "MMMM d, yyyy h:mm tt", disabled: true},
		    {name: "Your phone", id:  "phone", type: "text" , disabled: true}, 
		  ];
		  
		  var data = {
		    phone: localStorage.getItem("phone_number"),
		    start: args.e.start(),
		    end: args.e.end(),
		  };
		
		  var options = {
		    focus: "name"
		  };
		
		  DayPilot.Modal.form(form, data, options).then(function(modal) {
		      if (modal.canceled) {
		        return;
		      } 
		      // console.log(args.e)
		      DayPilot.Http.ajax({
		        url: "http://host.docker.internal:5007/appointments/update",
		        method: 'PUT',
		        data: {"phone": modal.result.phone, "appointment_id": args.e.data.id},
		        success: function(ajax) {
		          args.e.data.tags.status = "waiting";
		          calendar.events.update(args.e.data);
		        }
		      })
		  });
		
		};
		calendar.init();
		
		loadEvents();
		
	</script>
</body>
</html>
