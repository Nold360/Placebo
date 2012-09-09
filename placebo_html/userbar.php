<?php
	include "./inc/inc_user.php";	

	if($_SESSION["USER"] == true) {
		echo "&rarr; <a href=./index.php?site=search>Search</a><br>";
		if($_SESSION["STATUS"] == 2) {
			echo "&rarr; <a href=./index.php?site=add_host>Add Host</a><br>";
		}
		echo "<br>&rarr; <a href=./backend/logout.php>Logout</a><br>";
		echo "&rarr; <a href=index.php?site=chpasswd>Change Password</a>";
	} else {
		echo("  <form action=./backend/login.php method=post>
				Username <input type=text name=username>
				<br>Password &nbsp;<input type=password name=password>
				<br><input type=submit value=Login>
				</form>");	
	}
?>
