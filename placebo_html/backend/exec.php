<?php
	include "../inc/inc_user.php";
	include "../inc/inc_system.php";
	
	if($_SESSION["USER"] == true && $_SESSION["STATUS"] >= 1) {
		if(!isset($_POST["hostname"])) {
			header("Location: "+$_SERVER["HTTP_REFERER"]);
		}

		switch($_POST["action"]) {
			case "scan": scan_host($_POST["hostname"], $_POST["path"]); break;
			case "update": update_host($_POST["hostname"]); break;
			case "add": if($_SESSION["STATUS"] == 2) add_host($_POST["hostname"]); break;
			case "get": get_config_parameter($_POST["hostname"], $_POST["parameter"]); break;
			case "set": if($_SESSION["STATUS"] == 2) {
						set_config_parameter($_POST["hostname"], $_POST["parameter"], $_POST["value"]);
					} 
					header("Location: ../index.php?details=".$_POST["id"]); 
					die();	
			case "ping": get_client_status($_POST["hostname"]); break;
		}
	}	
	header("Location: ".$_SERVER['HTTP_REFERER']);
?>
