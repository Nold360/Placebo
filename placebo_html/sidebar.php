<?php
	include "./inc/inc_user.php";	
	include "./inc/inc_config.php";

	if($_SESSION["USER"] == true) {
		$query = "SELECT ID, Hostname FROM client ORDER BY Hostname ASC;";
		$result = mysql_query($query);
		
		echo "<li>";
		while(($row=mysql_fetch_array($result)) != null) {
			echo "<lu><img id=icon src=./gfx/computer.png> <a href=index.php?details=".$row["ID"].">".$row["Hostname"]."</a></lu><br>";
		}
		echo "</li>";
	} else {

	}
?>
