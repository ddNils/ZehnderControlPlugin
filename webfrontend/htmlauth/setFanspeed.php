<?php
if (isset($_GET('duration')) {
    // set duration as integer
    $duration = $_GET['duration'];
    if ($duration > 0 && $duration < (24 * 3600)) {
        startFanspeedPython($duration);
    } else {
        startFanspeedPython();
    }

} else {
    startFanspeedPython()
}

function startFanspeedPython($dur = 1800) {
    $command = escapeshellcmd('REPLACELBPBINDIR/startBoosts.py --configfile=$LBPCONFIG/REPLACEBYSUBFOLDER/pluginconfig.cfg');
    
    
}

?>