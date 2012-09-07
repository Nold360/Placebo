<?php
stream_set_blocking($stream, 0); 

function scan_host($hostname, $path) {
	if(isset($hostname)) {
		exec("sudo /usr/bin/python /usr/local/bin/placebos2c.py scan:".$path." ".$hostname." &> /dev/null &");
		return 0;
	} else {
		return 1;
	}
}


function update_host($hostname) {
	if(isset($hostname)) {
		exec("sudo /usr/bin/python /usr/local/bin/placebos2c.py update ".$hostname." &> /dev/null &");
		return 0;
	} else {
		return 1;
	}
}

function add_host($hostname) {
	if(isset($hostname)) {
		exec("sudo /usr/bin/python /usr/local/bin/placebos2c.py add ".$hostname." &> /dev/null &");
		return 0;
	} else {
		return 1;
	}
}
?>
