<?php
	include "../inc/inc_user.php";
	include "../inc/inc_config.php";

	if($_SESSION["USER"] == true && $_SESSION["STATUS"] == 2) {
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
	} else if($_POST["action"]=="change_passwd" && isset($_POST["oldPassword1"]) && isset($_POST["oldPassword2"])  && isset($_POST["newPassword"])) {
		if(trim($_POST["oldPassword1"]) == trim($_POST["oldPassword2"])) {
			$id = $_SESSION["USERID"];
			$query = "SELECT Password from user WHERE ID = ".$_SESSION["USERID"]." LIMIT 1;";
			$row = mysql_fetch_array(mysql_query($query));
			if($row["Password"] == sha1(trim($_POST["oldPassword1"]))) {
				$query = "UPDATE `placebo`.`user` SET `Password` = '".sha1($_POST['newPassword'])."'
                	                  WHERE `user`.`ID` = ".$id."
                	                  LIMIT 1 ;";
				mysql_query($query);
				$RET=0;
			} else {
				$RET=1;
			}
		} else {
			$RET=2;
		}
	} 	
	header("Location: ".$_SERVER["HTTP_REFERER"]."&ret=".$RET);
?>
