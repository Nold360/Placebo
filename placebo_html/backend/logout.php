<?php
	session_start();
	$_SESSION["USER"] = false;
	$_SESSION["USERID"] = false;
	$_SESSION["NAME"]=false;
	$_SESSION["VORNAME"]=false;
	$_SESSION["USERNAME"]=false;
	session_destroy();
	header("Location: ../index.php");
?>