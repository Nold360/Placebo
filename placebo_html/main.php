<?php
	include "./inc/inc_user.php";	
	include "./inc/inc_config.php";
	include "./inc/inc_content.php";
	
	echo '<div id="Content">';
	if($_SESSION["USER"] == true) {
		if(isset($_GET["details"]) && is_numeric($_GET["details"])) {
			show_client_details($_GET["details"], $_GET["report_id"]);
		} else if(isset($_GET["site"]) && $_GET["site"] == "chpasswd") {
			show_passwd_form();
		} else if(isset($_GET["site"]) && $_GET["site"] == "search") {
			show_search_form($_GET["hostname"]);
		} else if(isset($_GET["site"]) && $_GET["site"] == "add_host") {
			show_add_host_form();	
		} else if(isset($_GET["site"]) && $_GET["site"] == "mod_users") {
			show_mod_users();
		} else if(isset($_GET["site"]) && $_GET["site"] == "delete_host" && isset($_GET["id"]) && is_numeric($_GET["id"])) {
			delete_host($_GET["id"]);
		} else  {
			echo "<h2>Clientlist</h2>";
			show_client_list();
		}
	} else {
		echo "<h2>Please login</h2>";
	}
	
	echo '</div>';  
	mysql_close($db);
?>

