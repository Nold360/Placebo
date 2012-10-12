<?php
	include "./inc/inc_user.php";	

	if($_SESSION["USER"] == true) {
		echo "<a href=./index.php?site=search><img id=icon src=./gfx/search.png> Search</a><br>";
		if($_SESSION["STATUS"] == 2) {
			echo "<a href=./index.php?site=add_host><img id=icon src=./gfx/add.png> Add Host</a><br>";
			echo "<a href=./index.php?site=mod_users><img id=icon src=./gfx/edit.png> Modify Users</a><br>";
		}
		echo "<div style='position: fixed; top: 0; right: 5px;'><a href=index.php?site=chpasswd><img id=icon src=./gfx/reload.png> Change Password </a>";
		echo "<a style='margin-left: 10px;' href=./backend/logout.php><img id=icon src=./gfx/exit.png> Logout</a></div>";
	} else {
	}
?>
