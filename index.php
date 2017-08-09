<?php



?>


<h1>
Getting Todays MLB Info. Please wait.
</h1>

<?php

function run_cmd_with_output($cmd){

    $descriptorspec = array(
       0 => array("pipe", "r"),   // stdin is a pipe that the child will read from
       1 => array("pipe", "w"),   // stdout is a pipe that the child will write to
       2 => array("pipe", "w")    // stderr is a pipe that the child will write to
    );
    flush();
    $process = proc_open($cmd, $descriptorspec, $pipes, realpath('./'), array());
    echo "<pre>";
    if (is_resource($process)) {
        while ($s = fgets($pipes[1])) {
            print $s;
            flush();
        }
    }
    echo "</pre>";

}


ini_set('display_startup_errors', 1);
ini_set('display_errors', 1);
error_reporting(-1);

echo "<b>TEST</b>";
$cmd = 'ls ./';

run_cmd_with_output($cmd);

$cmd = 'source ./bin/activate && python scrape_espn.py';

run_cmd_with_output($cmd);



?>



//<?php
//
//
//
//?>
//
//
//<h1>
//Getting Todays MLB Info. Please wait.
//</h1>
//
//<?php
//
//print `echo /usr/bin/php -q scrape.php | at now`;
//
//
//?>
//
