<?php
	include "../inc/inc_user.php";
	include "../inc/inc_config.php";
	
	if($_SESSION["USER"] == true && $_SESSION["STATUS"] == 2) {
		$id = $_POST["id"];
		
		$query = "DELETE FROM client WHERE ID = ".$id." LIMIT 1;";
		mysql_query($query);
		$query = "DELETE FROM report WHERE Client_ID = ".$id.";";
		mysql_query($query);
		$query = "DELETE FROM signature WHERE Client_ID = ".$id.";";
		mysql_query($query);
	}
	
	header("Location: ../index.php");
?>
