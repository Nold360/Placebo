<?php
    function loginSuccess($username, $password) {
        include "inc_config.php";

        $query="select ID, Username, Password, Status from user where Username='".$username."'
            and Password='".$password."' limit 1";
			
        $result=mysql_query($query);
        $row=mysql_fetch_array($result);
	

        if(!isset($row["ID"])
                || trim($row["Username"])!=trim($username)
                || trim($row["Password"])!=trim($password)) {
			
            return false;
        } else {
            session_start();
            
            $_SESSION["USER"]=true;
            $_SESSION["USERID"]=$row["ID"];
			$_SESSION["USERNAME"]=$row["Username"];
			$_SESSION["STATUS"]=$row["Status"];
			
            return true;
        }
        mysql_close($db);
    }
?>
