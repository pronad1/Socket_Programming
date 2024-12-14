<?php

if($_SERVER['REQUEST_METHOD']=='POST'){
    include 'connect.php';
    $username=$_POST['username'];
    $password=$_POST['password'];

    $sql="insert into `registration`(username,password) values('$username','$password')";

    $result=mysqli_query($con,$sql);

    if($result){
        echo "Data inserted successfully.";
    }else{
        die(mysqli_error($con));
    }
}

?>




<!doctype html>
<html lang="en">

<head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.1.3/dist/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">

    <title>login_logout Page</title>
</head>

<body>
    <div class="container" mt-5>
<h1 class="text-center">Sign Up Page</h1>
        <form action="sign.php" method="post"> 
            <div class="form-group">
                <label for="exampleInputEmail1">Name</label>
                <input type="username" class="form-control" placeholder="Enter your username" name="username">
            </div>
            <div class="form-group">
                <label for="exampleInputPassword1">Password</label>
                <input type="password" class="form-control" placeholder="Enter your Password" name="password">
            </div>
            <button type="submit" class="btn btn-primary w-100">Submit</button>
        </form>

    </div>
</body>

</html>