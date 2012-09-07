<?php
	include "./inc/inc_user.php";
	
	echo "<html><head><title>WMW - TI16</title><link href=style.css rel=stylesheet type=text/css></head><body bgcolor=lightgrey><div id=header><font size=6px>Wer-Macht-Was bei TI16?</font> <a href=index.php>Zurück</a></div>";
	
	echo '<div id=pwChange>';
	echo "<form id=pwChange action=./backend/change_password.php method=post>";
	echo "<br>Altes Passwort: &nbsp;&nbsp;<input type=password name=oldPassword>";
	echo "<br>Neues Passwort: <input type=password name=newPassword>";
	echo "<br><input type=submit value=Ändern></form>";
	
	echo "</body></html>";
?>