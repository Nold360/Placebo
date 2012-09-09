<?php

function show_client_list($hostname=null) {
	if(isset($hostname)) { 
		$query="SELECT `client`.`ID` , `client`.`Hostname` , `signature`.`Date` AS signature_date
				FROM client
				LEFT JOIN signature ON client.ID = signature.Client_ID
				WHERE hostname LIKE '%".$hostname."%'";
		$result = mysql_query($query);
		
		if(mysql_num_rows($result) == 1) { //Is there a single host 
			$row = mysql_fetch_array($result);
			show_client_details($row["ID"]);
			return 0;
		} else if(mysql_num_rows($result) == 0) { //No Hosts
				echo "No host found!";
				return 1;
		} else { //More then one host without signatures
			$query="SELECT `client`.`ID` , `client`.`Hostname` , `signature`.`Date` AS signature_date
				FROM client
				LEFT JOIN signature ON client.ID = signature.Client_ID
				WHERE hostname LIKE '%".$hostname."%'";	
		}
	} else { //Just list every host
		$query="SELECT `client`.`ID` , `client`.`Hostname` , `signature`.`Date` AS signature_date
				FROM client
				LEFT JOIN signature ON client.ID = signature.Client_ID;";
	}
	

	echo "<table id=content border=1 bgcolor=white><tr bgcolor=#9999FF><th>Status</th><th>Hostname</th><th>Last Scan-Path</th><th>Last Scan-Date</th><th>Signature Date</th>";
	
	$result=mysql_query($query);
	while(($row=mysql_fetch_array($result)) != null) {
		$color="green";
		$er_text="OK";
		$query="SELECT `report`.`Path` , `report`.`Report`
				FROM report
				WHERE ((`report`.`Client_ID` =".$row['ID'].") AND (`report`.`Report` LIKE '%FOUND%')) 
				limit 1";
				
		$result2=mysql_query($query);
		$has_virus=mysql_fetch_array($result2);
	
		if(isset($has_virus['Path'])) {
			$color="red";
			$er_text="<blink>! VIRUS !</blink>";
		} else {
			$query = "SELECT Report FROM report WHERE Client_ID = ".$row['ID'].";";
			$result2 = mysql_query($query);
			$scan = mysql_fetch_array($result2);
			
			if(empty($scan)) {
				$color = "blue";
				$er_text = "Unknown";
			} else {
				$query="SELECT report.Path, report.Date
						FROM report
						WHERE report.Client_ID = ".$row['ID']."
						ORDER BY report.Date DESC
						LIMIT 1;"; 
				
				$result2=mysql_query($query);
				$last_scan=mysql_fetch_array($result2);
			}
		}
		
		if(empty($last_scan)) {
			$last_scan["Path"] = "";
			$last_scan["Date"] = "";
		}

		echo "<tr><td bgcolor=".$color."><center>".$er_text."</center></td><td><a href=./index.php?details=".$row["ID"].">".$row["Hostname"]."</a></td><td>".$last_scan["Path"]."</td><td>".$last_scan["Date"]."</td><td>".$row["signature_date"]."</td>";		
		echo "</tr>";
	}
	echo '</table>';
}

function show_client_details($id) {
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
				echo "<br><a href=index.php>Back</a>";
				return 1;
			}
			
			echo "<a href=index.php>Index</a> &rarr; <b>".$hostname."</b> (".$ip.")<br><br>";
									
			$query = "SELECT Signature, Date
					  FROM signature
					  WHERE Client_ID =".$id.";";
					  
			$result=mysql_query($query);
			
			
			if($_SESSION["STATUS"] == 2) {
				echo "<form action=./backend/exec.php method=post><input name=hostname type=hidden value=".$hostname."><input name=action value=update type=hidden><input type=submit value='Update Signatures'></form>";
			}
			
			//Signaturen anzeigen
			echo "<table id=content border=1 bgcolor=#FFFFFF><tr bgcolor=#9999FF><th>Signature</th><th>Date</th>";
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
			
			echo "<table id=content border=1 bgcolor=white><tr bgcolor=#9999FF><th>Rescan</th><th>Scan-Path</th><th>Date</th><th>Report</th></tr>";
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
}

function show_passwd_form() {
	echo "<h2>Change Password</h2>";
	echo "<form id=pwChange action=./backend/change_password.php method=post>";
	echo "Old Password: &nbsp;&nbsp;<input type=password name=oldPassword>";
	echo "<br>New Password: <input type=password name=newPassword>";
	echo "<br><input type=submit value=Change></form>";	
}

function show_search_form($hostname) {
		echo "<h2>Search</h2>";
		
		echo "<form action=./index.php?site=search method=get>";
		echo "<input type=hidden name=site value=search>";
		echo "Hostname <input type=text name=hostname value=".$hostname.">";
		echo "<br><input type=submit value=Search></form><br>";
		
		if(isset($hostname)) {
			show_client_list($hostname);
		}
}

function show_add_host_form() {
	echo "<h2>Add new Host</h2>";
	echo "<form id=pwChange action=./backend/exec.php method=post>";
	echo "<input type=hidden name=action value=add>";
	echo "Hostname <input type=text name=hostname>";
	echo "<br><input type=submit value=Add></form>";	
}
?>
