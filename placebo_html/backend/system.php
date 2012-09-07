<?php

function scan_host($hostname, $path="/") {
	if(isset($hostname)) {
		system("/usr/local/bin/placebos2c.py scan:"+$path+" "+$hostname);
	} else {
		return 1;
	}
}


?>