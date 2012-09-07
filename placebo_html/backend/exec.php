<?php
	include "../inc/inc_user.php";
	include "../inc/inc_system.php";
	
	if(!isset($_POST["hostname"])) {
		header("Location: "+$_SERVER["HTTP_REFERER"]);
	}


	if($_POST["action"] == "scan") {
		scan_host($_POST["hostname"], $_POST["path"]);
	} else if($_POST["action"] == "update") {
		update_host($_POST["hostname"]);
	} else if($_POST["action"] == "add") {
		add_host($_POST["hostname"]);
	}	
	
	header("Location: ".$_SERVER['HTTP_REFERER']);
?>
