<?php
	include "inc_config.php";
	
	echo '<div id="Content">';
	
	$query="SELECT `client`.`ID` , `client`.`Hostname` , `signature`.`Date` AS signature_date
			FROM client, signature
			GROUP BY client.ID
			ORDER BY `client`.`ID` ASC";
			
	$result=mysql_query($query);
	echo "<table id=content border=1 bgcolor=white><tr bgcolor=lightblue><th>Status</th><th>Hostname</th><th>Last Scan-Path</th><th>Last Scan</th><th>Signature Date</th>";
	
	while(($row=mysql_fetch_array($result)) != null) {
		$color="green";
		$er_text="OK";
		$query="SELECT `report`.`Path` , `report`.`Report`
				FROM report
				WHERE ((`report`.`Client_ID` =".$row['ID'].") AND (`report`.`Report` LIKE '%FOUND%')) 
				limit 1";
				
		$result=mysql_query($query);
		$new_row=mysql_fetch_array($result);
	
		if(isset($new_row['Path'])) {
			$color="red";
			$er_text="<blink>! VIRUS !</blink>";
		}
	
		$query="SELECT report.Path, report.Date
			FROM report
			WHERE report.Client_ID = ".$row['ID']."
			ORDER BY report.Date DESC
			LIMIT 1;"; 
		
		$result=mysql_query($query);
                $last_scan=mysql_fetch_array($result);


		echo "<tr><td bgcolor=".$color."><center>".$er_text."</center></td><td><a href=./details.php?id=".$row["ID"].">".$row["Hostname"]."</a></td><td>".$last_scan["Path"]."</td><td>".$last_scan["Date"]."</td><td>".$row["signature_date"]."</td>";		
		echo "</tr>";
	}
	echo '</table>';
	echo '</div>';  
	mysql_close($db);
?>
