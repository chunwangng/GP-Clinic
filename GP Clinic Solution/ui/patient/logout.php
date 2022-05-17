<?php unset($_SESSION['phone_number']) ?>
<?php 
if (! isset($_SESSION['phone_number'])){
    echo "You have succesfully logged out";
    header('Location: index.html');
}
 ?>