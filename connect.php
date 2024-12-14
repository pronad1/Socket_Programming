<?php

$con=new mysqli('localhost','root','','login_logout');

if(!$con){
    die("Connection Failed: ".mysqli_connect_error());
}
else{
    echo "Connection Successfully";
}



?>
