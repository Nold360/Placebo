<?php
	include "./inc/inc_config.php";
	include "./inc/inc_user.php";
	
	echo ("	<html><head><title>Placebo</title>
			<link href=style.css rel=stylesheet type=text/css></head>
			<body>
			<div id=header><font size=6px><a href=index.php>Placebo</a></font>");
			
			if($_SESSION["USER"] == true) {
				echo "<a href=change_password_form.php> Passwort ändern</a>";
				echo "<form id=logout action=./backend/logout.php method=post><input type=submit value=Logout></form><br><br>";
			}
			
			$id = $_GET["id"];
			
			$query = "SELECT Hostname, IP
					  FROM client
					  WHERE ID =".$id."
					  LIMIT 1;";
					  
			$result=mysql_query($query);
			$row=mysql_fetch_array($result);	
			
			if(!empty($row)) {
				$hostname = $row["Hostname"];
				$ip = $row["IP"];
			} else {
				echo "ERROR: Didn't find host!";
				die();
			}
			
			echo "<b>".$hostname."</b><br>";
			echo $ip."<br><br>";
			
			$query = "SELECT Signature, Date
					  FROM signature
					  WHERE Client_ID =".$id.";";
					  
			$result=mysql_query($query);
			
			
			if($_SESSION["STATUS"] == 2) {
				echo "<form action=./backend/exec.php method=post><input name=hostname type=hidden value=".$hostname."><input name=action value=update type=hidden><input type=submit value=Update></form>";
			}
			
			//Signaturen anzeigen
			echo "<table id=content border=1 bgcolor=white><tr bgcolor=lightblue><th>Signature</th><th>Date</th>";
			while(($row=mysql_fetch_array($result)) != null) {
				echo "<tr><td>".$row["Signature"]."</td><td>".$row["Date"]."</td></tr>";
			}
			echo "</table><br><br>";
			
			$query = "SELECT Path, Report, Date
					  FROM report
					  WHERE Client_ID =".$id."
				  ORDER BY Date DESC;";	
					  
			$result=mysql_query($query);
			
			if($_SESSION["STATUS"] == 2) {
				echo "<form action=./backend/exec.php method=post>
					<input type=hidden name=hostname value=".$hostname.">
					Scan Path <input type=text name=path value=/> 
					<input name=action value=scan type=hidden>
					<input type=submit value=Scan></form>";
			}
			
			echo "<table id=content border=1 bgcolor=white><tr bgcolor=lightblue><th>Rescan</th><th>Scan-Path</th><th>Date</th><th>Report</th></tr>";
			while(($row=mysql_fetch_array($result)) != null) {
				if(strpos($row["Report"], "FOUND")) {
					$color = "red";
				} else {
					$color = "green";
				}
				echo "<tr bgcolor=".$color."><td>";
				
				if($_SESSION["STATUS"] == 2) {
					echo "<form action=./backend/exec.php method=post>
					<input type=hidden name=hostname value=".$hostname.">
					<input type=hidden name=path value=".$row["Path"].">
					<input name=action value=scan type=hidden>
					<input type=SUBMIT value=Rescan></form>
					</td>";
				}
				echo "<td>".$row["Path"]."</td><td>".$row["Date"]."</td><td>".str_replace("\n", "<br>", $row["Report"])."</td></tr>";
			}
			echo "</table>";
			echo "</div>";
?>
