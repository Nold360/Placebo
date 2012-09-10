<?php
	include "../inc/inc_user.php";
	include "../inc/inc_config.php";
	
	if($_SESSION["USER"] == true) {
		$id = $_POST["id"];
		$username = $_POST["username"];
		$name = $_POST["name"];
		$prename = $_POST["prename"];
		$status = $_POST["status"];
	
		$new_passwd = $_POST["passwd"];

		$delete = $_POST["delete"];

		if(isset($delete)) {
			$query = "DELETE FROM `placebo`.`user` 
				WHERE `user`.`ID` = ".$id." 
				AND `user`.`Username` = '".$username."' 
				AND `user`.`Name` = '".$name."'
				AND `user`.`Prename` = '".$prename."' 
				AND `user`.`Status` = '".$status."' 
				LIMIT 1";
			mysql_query($query);
		} else if(!empty($username) && !empty($name) && !empty($prename) && isset($status)) {
			if(isset($id) && is_numeric($id)) { //Change user
				if(!empty($new_passwd)) {
					$query = "UPDATE `placebo`.`user` SET `Username` = '".$username."',
								`Name` = '".$name."',
								`Prename` = '".$prename."',
								`Password` = '".sha1($new_passwd)."',
								`Status` = '".$status."' 
								WHERE `user`.`ID` = ".$id." 
								LIMIT 1 ;";
				} else {
					$query = "UPDATE `placebo`.`user` SET `Username` = '".$username."',
								`Name` = '".$name."',
								`Prename` = '".$prename."',
								`Status` = '".$status."' 
								WHERE `user`.`ID` = ".$id."
								LIMIT 1 ;";
				}
				mysql_query($query);
			} else { //Add new User
				if(!empty($new_passwd)) {
					$query = "INSERT INTO `placebo`.`user` (`ID`, `Username`, `Name`, `Prename`, `Password`, `Status`) 
								VALUES ('', '".$username."', '".$name."', '".$prename."', '".sha1($new_passwd)."', '".$status."');";
					mysql_query($query);
				}
			}
		}
	}
	
	header("Location: ".$_SERVER["HTTP_REFERER"]);
?>
