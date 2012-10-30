<?php
stream_set_blocking($stream, 0); 

function scan_host($hostname, $path) {
	if(isset($hostname)) {
		exec("/usr/bin/python /usr/local/bin/placebos2c.py scan:".$path." ".$hostname." &> /dev/null &");
		return 0;
	} else {
		return 1;
	}
}


function update_host($hostname) {
	if(isset($hostname)) {
		exec("/usr/bin/python /usr/local/bin/placebos2c.py update ".$hostname." &> /dev/null &");
		return 0;
	} else {
		return 1;
	}
}

function add_host($hostname) {
	if(isset($hostname)) {
		exec("/usr/bin/python /usr/local/bin/placebos2c.py add ".$hostname." &> /dev/null &");
		return 0;
	} else {
		return 1;
	}
}

function get_scan_processes($hostname) {
	if(isset($hostname)) {
		return shell_exec("ps -ef | grep placebos2c | grep -v grep | grep -v sudo  | awk '{print $10}' | cut -f2- -d:");
	} else {
		return 1;
	}
}

function get_config_parameter($hostname, $parameter) {
	if(isset($hostname) && isset($parameter)) {
		return shell_exec("/usr/bin/python /usr/local/bin/placebos2c.py get:".$parameter." ".$hostname." | tail -1");
	} else {
		return "ERR";
	}
}

function set_config_parameter($hostname, $parameter, $value) {
	if(isset($hostname) && isset($parameter) && isset($value)) {
		return shell_exec("/usr/bin/python /usr/local/bin/placebos2c.py set:".$parameter."=".$value." ".$hostname." | tail -1");
	} else {
		return "ERR";
	}
}

function get_client_status($hostname) {
        if(isset($hostname)) {
                exec("/usr/bin/python /usr/local/bin/placebos2c.py ping ".$hostname);
		return 0;
        } else {
                return 1;
        }
}

?>
