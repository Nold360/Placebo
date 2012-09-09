<?php
	include "./inc/inc_user.php";	
	include "./inc/inc_config.php";
	include "./inc/inc_content.php";
	
	echo '<div id="Content">';
	if(isset($_GET["details"]) && is_numeric($_GET["details"])) {
		show_client_details($_GET["details"]);
	} else if(isset($_GET["site"]) && $_GET["site"] == "chpasswd") {
		show_passwd_form();
	} else if(isset($_GET["site"]) && $_GET["site"] == "search") {
		show_search_form($_GET["hostname"]);
	} else if(isset($_GET["site"]) && $_GET["site"] == "add_host") {
		show_add_host_form();	
	} else if ($_SESSION["USER"] == true) {
		echo "<h2>Clientlist</h2>";
		show_client_list();
	} else {
		echo "Please login";
	}
	
	echo '</div>';  
	mysql_close($db);
?>

