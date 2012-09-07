<?php	
	include "../inc/inc_user.php";
    include "../inc/inc_config.php";
	include "../inc/inc_login.php";
	
	if(loginSuccess($_SESSION["USERNAME"], sha1($_POST["oldPassword"]))) {
		$query="UPDATE `placebo`.`user` SET `Passwort` = '".sha1($_POST['newPassword'])."' WHERE `benutzer`.`ID` =".$_SESSION['USERID'].";";
		
		mysql_query($query);
	}
	mysql_close($db);
	
	header("Location: ../index.php");
?>