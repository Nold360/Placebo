<?php
	include "../inc/inc_login.php";
	
	loginSuccess(strtolower($_POST["username"]), sha1($_POST["password"]));
	header("Location: ../index.php");
?>