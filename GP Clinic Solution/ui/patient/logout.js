function logout(){
    //unsert the session
    if (localStorage.getItem("staff_id")){
      localStorage.removeItem("staff_id");
      console.log("success")
    }
    
    if (localStorage.getItem("phone_number")){
      localStorage.removeItem("phone_number");
      console.log("success")
    }

    // redirect to php page for logout
    window.location = "logout.php";
  }