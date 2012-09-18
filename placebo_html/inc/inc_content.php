<?php

function show_client_list($hostname=null) {
	if(isset($hostname)) { 
		$query="SELECT `client`.`ID`
				FROM client
				WHERE hostname LIKE '%".$hostname."%'
				GROUP BY `client`.`ID`;";
		$result = mysql_query($query);
		
		if(mysql_num_rows($result) == 1) { //Is there a single host 
			$row = mysql_fetch_array($result);
			show_client_details($row["ID"]);
			return 0;
		} else if(mysql_num_rows($result) == 0) { //No Hosts
				echo "No host found!";
				return 1;
		}
	} 
	//Just list every host/List all hosts like the given Hostname
	if(!isset($hostname)) {
		$hostname="";
	}
	$query="SELECT `client`.`ID` , `client`.`Hostname` , `signature`.`Date` AS signature_date, 
			(SELECT report.Client_ID FROM report WHERE report.Client_ID = client.ID AND report.report LIKE '%FOUND%' LIMIT 1) AS virus,
			(SELECT report.path FROM report WHERE report.Client_ID = client.ID ORDER BY report.Date DESC LIMIT 1) AS report_path,
			(SELECT report.date FROM report WHERE report.Client_ID = client.ID ORDER BY report.Date DESC LIMIT 1) AS report_date	
		FROM client
		LEFT JOIN signature ON client.ID = signature.Client_ID
		WHERE client.Hostname LIKE '%".$hostname."%'
		GROUP BY `client`.`ID`;";
	
	

	echo "<table id=content bgcolor=white><tr bgcolor=#9999FF id=nohover><th>Status</th><th>Hostname</th><th>Last Scan-Path</th><th>Last Scan-Date</th><th>Signature Date</th>";
	
	$result=mysql_query($query);
	while(($row=mysql_fetch_array($result)) != null) {
		$color = "#009911";
		$er_text="OK";
	
		if(isset($row["virus"])) {
			$color = "#FF3700";
			$er_text="<blink>! VIRUS !</blink>";
		} else if(!isset($row["report_path"])) {
				$color = "#0099FF";
				$er_text = "Unknown";
		}

		echo "<tr><td bgcolor=".$color." align=center>".$er_text."</td><td align=center><a href=./index.php?details=".$row["ID"].">".$row["Hostname"]."</a></td>
			<td>".$row["report_path"]."</td><td align=center>".$row["report_date"]."</td><td align=center>".$row["signature_date"]."</td>";		
		echo "</tr>";
	}
	echo '</table>';
}

function show_client_details($id, $report_id=null) {
			include "inc_system.php";

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

			echo "<h2 style='margin-bottom: 0px'>Details of ".$hostname."</h2>";	
			echo "<div id=content style='border-bottom: 1px solid black;'><a title='Back to List' href=index.php><img alt='Index' id=icon style='margin-bottom: 2px;' src=./gfx/home.png>
				</a> &rarr; <img id=icon style='margin-bottom: 2px;' src=./gfx/computer.png> <b>".$hostname."</b> (".$ip.")";
			
			if( $_SESSION["STATUS"] == 2) {
				echo "<a title='Delete Host' href=index.php?site=delete_host&id=".$id."><img id=delete alt='Delete Host' src=./gfx/delete.png></a>";
			}			
			echo "</div><br>";	
					
			$query = "SELECT Signature, Date
					  FROM signature
					  WHERE Client_ID =".$id.";";
					  
			$result=mysql_query($query);
			
			
			if($_SESSION["STATUS"] >= 1) {
				echo "<form action=./backend/exec.php method=post><input name=hostname type=hidden value=".$hostname.">
					<input name=action value=update type=hidden><button id=submit type=submit><img style='vertical-align: top;' src=./gfx/reload.png> Update Signatures</button></form>";
			}
			
			//Show Signatures
			echo "<div id=content><table id=signatures bgcolor=#FFFFFF><tr bgcolor=#9999FF id=nohover><th width=50%>Signature</th><th>Date</th>";
			while(($row=mysql_fetch_array($result)) != null) {
				echo "<tr><td>".$row["Signature"]."</td><td align=center>".$row["Date"]."</td></tr>";
			}
			echo "</table>";
			
			$query = "SELECT ID, Path, Report, Date
				  FROM report
				  WHERE Client_ID =".$id."
				  ORDER BY Date DESC;";	
					  
			$result=mysql_query($query);
			
			//Show running scan Processes
			$ret = get_scan_processes($hostname);
			echo "<table id=scans bgcolor=white><tr bgcolor=#9999FF id=nohover><th>Running Operations:</th></tr>";
			foreach (explode("\n", $ret) as $scan) {
				if(!empty($scan)) {
					echo "<tr><td><center>".$scan."</center></td></tr>";
				}
			}
			echo "</table>";
			echo "</div>";

			echo "<br><br><br><br><br><br><br><br>";
			if($_SESSION["STATUS"] >= 1) {
				echo "<form action=./backend/exec.php method=post>
					<input type=hidden name=hostname value=".$hostname.">
					Scan Path <input type=text name=path value=/> 
					<input name=action value=scan type=hidden>
					<input id=submit type=submit value=Scan></form>";
			}
			
			//Show Scan-Reports
			echo "<table id=content bgcolor=white><tr bgcolor=#9999FF id=nohover><th width=1px>Rescan</th><th width=20%>Scan-Path</th><th width=20%>Date</th><th>Report</th></tr>";
			while(($row=mysql_fetch_array($result)) != null) {
				if(strpos($row["Report"], "FOUND")) {
					$color = "#FF3700";
				} else {
					$color = "#009911";
				}

				echo "<tr bgcolor=".$color."><td align=center>";
				if($_SESSION["STATUS"] >= 1) {
					echo "<form action=./backend/exec.php method=post>
					<input type=hidden name=hostname value=".$hostname.">
					<input type=hidden name=path value=".$row["Path"].">
					<input name=action value=scan type=hidden>
					<button type=submit id=submit><img style='vertical-align: top;' src=./gfx/reload.png></button></form>
					</td>";
				} 

				if(isset($report_id) && $report_id == $row["ID"]) {
					echo "<td>".$row["Path"]."</td><td align=center>".$row["Date"]."</td><td>".str_replace("\n", "<br>", $row["Report"])."</td></tr>";
				} else {
					echo "<td>".$row["Path"]."</td><td align=center>".$row["Date"]."</td><td>
						<form action=index.php method=get><input type=hidden name=details value=".$id.">
						<input type=hidden name=report_id value=".$row["ID"].">
						<button type=submit id=submit><img style='vertical-align: top;' src=./gfx/info.png> Show Report</button></form></td></tr>";
				}
			}
			echo "</table>";

}

function show_passwd_form() {
	echo "<h2>Change Password</h2>";
	echo "<form id=pwChange action=./backend/change_password.php method=post>";
	echo "Old Password: &nbsp;&nbsp;<input type=password name=oldPassword>";
	echo "<br>New Password: <input type=password name=newPassword>";
	echo "<br><input id=submit type=submit value=Change></form>";	
}

function show_search_form($hostname) {
		echo "<h2>Search</h2>";
		
		echo "<form action=./index.php?site=search method=get>";
		echo "<input type=hidden name=site value=search>";
		echo "Hostname <input type=text name=hostname value=".$hostname.">";
		echo " <input id=submit type=submit value=Search></form><br>";
		
		if(isset($hostname)) {
			show_client_list($hostname);
		}
}

function show_add_host_form() {
	echo "<h2>Add new Host</h2>";
	echo "<form id=pwChange action=./backend/exec.php method=post>";
	echo "<input type=hidden name=action value=add>";
	echo "Hostname <input type=text name=hostname>";
	echo " <input id=submit type=submit value=Add></form>";	
}

function show_mod_users() {
	echo "<h2>Modify Users</h2>";
	
	$query = "SELECT ID, Username, Name, Prename, Status FROM user ORDER BY Name ASC;";
	$result = mysql_query($query);
	
	echo "<table id=content><tr bgcolor=lightblue id=nohover><th>Username</th><th>Name</th><th>Prename</th><th>Status</th><th>New Password</th><th>Apply</th></tr>";
	echo "<form action=./backend/mod_user.php method=post><tr>
	<td><input id=user type=text name=username></td>
	<td><input id=user type=text name=name></td>
	<td><input id=user type=text name=prename></td>
	<td><center><input type=radio name='status' value='0'>Guest
        <input type=radio name='status' value='1'>User
        <input type=radio name='status' value='2' checked=checked>Admin</center></td>
	<td><input id=user type=text name=passwd></td>
	<td><input id=submit type=submit value=Create New></td></tr></form>";
	
	while(($row=mysql_fetch_array($result)) != null) {
		$checked0="";
		$checked1="";
		$checked2="";
                if($row["Status"] == 0) {
                        $checked0="checked=checked";
                } else if($row["Status"] == 1) {
                        $checked1="checked=checked";
                } else if($row["Status"] == 2) {
                        $checked2="checked=checked";
                }

		echo ("<form action=./backend/mod_user.php method=post>
		<input type=hidden name=id value=".$row["ID"].">
		<tr>
		<td><input id=user type=text name=username value=".$row["Username"]."></td>
		<td><input id=user type=text name=name value=".$row["Name"]."></td>
		<td><input id=user type=text name=prename value=".$row["Prename"]."></td>
		<td><center><input type=radio name='status' value='0' ".$checked0.">Guest 
		<input type=radio name='status' value='1' ".$checked1.">User 
		<input type=radio name='status' value='2' ".$checked2.">Admin</center></td>
		<td><input id=user type=text name=passwd><td><input id=submit type=submit value=Apply>
		<input id=delete type='checkbox' name='delete' value='1'><font id=delete>Delete </font></form>
		</td></tr>"); 
	}
	echo "</table>";
}

function delete_host($id) {
	$query="SELECT Hostname FROM client where ID = ".$id." LIMIT 1;";
	$row=mysql_fetch_array(mysql_query($query));

	echo "<h2>Delete Host</h2>";
	echo "Are you shure that you want to delete the Host: ".$row["Hostname"]."?<br><br>";
	echo "<table><tr id=login><td id=login><form action=./backend/del_host.php method=post>
        <input type=hidden name=id value=".$id.">
	<input style='background: red;' type=submit value='Yes' id=submit>
	</form></td><td id=login width=50px></td>"; 
	echo "<td id=login><form action=".$_SERVER["HTTP_REFERER"]." method=post><input style='background: lightgreen;' type=submit id=submit value=No></form></td></tr></table>";
}

?>
