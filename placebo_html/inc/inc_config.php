<?php
	//MySQL Config-File 0.2BETA by Gerrit Pannek
	//Please change this stuff:
	
	$dbhost = "localhost"; //in 99% it's localhost
	$dbuser = "root"; //Username
	$dbpass = "password"; //Password for the user
	$dbname = "placebo"; //name of the Database
	
	//Do NOT change anything under this!
	$db = @mysql_connect($dbhost, $dbuser, $dbpass);
    @mysql_select_db($dbname, $db);

    $dbhost = ""; 
	$dbuser = ""; 
	$dbpass = "";
	$dbname = "";
?>
