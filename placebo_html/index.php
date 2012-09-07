<?php
	include "./inc/inc_user.php";
	
	echo ("	<html><head><title>Placebo</title>
			<link href=style.css rel=stylesheet type=text/css></head>
			<body>
			<div id=header><font size=6px>Placebo</font>");
			
			if($_SESSION["USER"] == true) {
				echo "<a href=change_password_form.php> Passwort ändern</a>";
				echo "<form id=logout action=./backend/logout.php method=post><input type=submit value=Logout></form><br><br>";

			}
			
	
	if($_SESSION["USER"] != true) {
		echo("
				<br><div id=Content>Please login:<form action=./backend/login.php method=post>
				<br>Username &nbsp;<input type=text name=username>
				<br>Password <input type=password name=password>
				<br><input type=submit value=Login>
				</form></div>");
	} else {
		include "./inc/inc_content.php";
	}
	echo "</div>";
	echo "</body></html>";
?>