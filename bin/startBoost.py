
import argparse
import socket
import logging
import configparser
from pycomfoconnect import ComfoConnect
from pycomfoconnect import Bridge
    
    # seconds = 120
    # s = str("{:012x}".format(seconds))
    # r"\x" + r"\x".join(s[n : n+2] for n in range(0, len(s), 2))

    #comfoconnect.cmd_rmi_request(b'\x84\x15\x01\x06\x00\x00\x00\x00\x78\x00\x00\x00\x03') 
    
local_name = 'Loxberry'
local_uuid = bytes.fromhex('00000000000000000000000000000005')

def bridge_discovery(ip):
    ## Bridge discovery ################################################################################################

    # Method 1: Use discovery to initialise Bridge
    # bridges = Bridge.discover(timeout=1)
    # if bridges:
    #     bridge = bridges[0]
    # else:
    #     bridge = None

    # Method 2: Use direct discovery to initialise Bridge
    bridges = Bridge.discover(ip)
    if bridges:
        bridge = bridges[0]
    else:
        bridge = None

    # Method 3: Setup bridge manually
    # bridge = Bridge(args.ip, bytes.fromhex('0000000000251010800170b3d54264b4'))

    if bridge is None:
        print("No bridges found!")
        exit(1)

    print("Bridge found: %s (%s)" % (bridge.uuid.hex(), bridge.host))
    bridge.debug = True

    return bridge


def callback_sensor(var, value):
    ## Callback sensors ################################################################################################    
    print("CALLBACK: %s = %s" % (var, value))


def main(args):
    print("starting main")
    seconds = 120
    if args.duration:
        seconds = int(args.duration)

    """
    Check if running in debug mode
    """
    if args.debug:
        import debugpy
        print("running in debug mode - waiting for debugger connection on {0}:{1}".format(args.debugip, args.debugport))
        debugpy.listen((args.debugip, args.debugport))
        debugpy.wait_for_client()

    pluginconfig = configparser.ConfigParser()
    pluginconfig.read(args.configfile)
    
    print("reading config, has sections: " + ", ".join(pluginconfig.sections()))

    if pluginconfig.has_section("ZehnderCtrl"):
        pin = pluginconfig.get('ZehnderCtrl', 'zehnderPIN')
        zehnderIP = pluginconfig.get('ZehnderCtrl', 'zehnderIP')
        pluginEnabled = pluginconfig.get('ZehnderCtrl', 'enabled')
    
    # Discover the bridge
    bridge = bridge_discovery(zehnderIP)

    ## Setup a Comfoconnect session  ###################################################################################

    comfoconnect = ComfoConnect(bridge, local_uuid, local_name, pin)
    comfoconnect.callback_sensor = callback_sensor

    print("Connecting to zehnder bridge")

    try:
        # Connect to the bridge
        # comfoconnect.connect(False)  # Don't disconnect existing clients.
        comfoconnect.connect(True)  # Disconnect existing clients.

    except Exception as e:
        print('ERROR: %s' % e)
        exit(1)
    
    ## Executing functions #############################################################################################
    
    seconds = 280
    s = str("{:012x}".format(seconds))
    #duration_bytes = r"\x" + r"\x".join(s[n : n+2] for n in range(0, len(s), 2))
    duration_bytes = r"\x" + r"\x".join(s[n : n+2] for n in range(0, len(s), 2))

    bytestring = '\x84\x15\x01\x06' + duration_bytes + '\x00\x00\x03'

    print("Bytestring to send to zehnder: " + bytestring)
    
    s_new: bytes = (b'\x84\x15\x01\x06' + bytes(duration_bytes, encoding="raw_unicode_escape") + b'\x00\x00\x03')
    
    # 8415 0106 0000 0000 5802 0000 03	Boost mode: start for 10m (= 600 seconds = 0x0258)
    comfoconnect.cmd_rmi_request(s_new) 
  
   #  comfoconnect.cmd_rmi_request(b'\x84\x15\x01\x06' + duration_bytes + b'\x00\x00\x03')

    # comfoconnect.cmd_rmi_request(CMD_FAN_MODE_AWAY)  # Go to away mode
    # comfoconnect.cmd_rmi_request(CMD_FAN_MODE_LOW)  # Set fan speed to 1
    # comfoconnect.cmd_rmi_request(CMD_FAN_MODE_MEDIUM)  # Set fan speed to 2

    # comfoconnect.cmd_rmi_request(CMD_FAN_MODE_HIGH)  # Set fan speed to 3

    ## Closing the session #############################################################################################

    print('Disconnecting...')
    comfoconnect.disconnect()

    

if __name__ == "__main__":
    """
    Parse commandline arguments
    """
    parser = argparse.ArgumentParser(description="Loxberry ZehnderCtrl Plugin.")

    arggroup = parser.add_argument_group("duration")

    arggroup.add_argument("--duration",
                    dest="duration",
                    default=1800,
                    action="store",
                    help="Duration in seconds (default=1800 / 30min)")
    
    debugroup = parser.add_argument_group("debug")

    debugroup.add_argument("--debug", 
                        dest="debug",
                        default=False,
                        action="store_true",
                        help="enable debug mode")

    debugroup.add_argument("--debugip", 
                        dest="debugip",
                        default=socket.gethostbyname(socket.gethostname()),
                        action="store",
                        help="Local IP address to listen for debugger connections (default={0})".format(socket.gethostbyname(socket.gethostname())))

    debugroup.add_argument("--debugport", 
                        dest="debugport",
                        default=5678,
                        action="store",
                         help="TCP port to listen for debugger connections (default=5678)")
   
    
    loggroup = parser.add_argument_group("log")

    loggroup.add_argument("--logfile", 
                        dest="logfile",
                        default="zehnderCtrl.log",
                        type=str,
                        action="store",
                        help="specifies logfile path")

    loggroup = parser.add_argument_group("config")

    loggroup.add_argument("--configfile", 
                        dest="configfile",
                        default="zehnderCtrlConfig.cfg",
                        type=str,
                        action="store",
                        help="specifies plugin configuration file path")

    args = parser.parse_args()

    """
    # logging configuration
    """
    logging.getLogger().setLevel(logging.DEBUG)
    logging.basicConfig(filename=args.logfile,
                        filemode='w', 
                        level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',)

    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.NOTSET)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console) 
    logging.info("using plugin log file {0}".format(args.logfile))

    """
    call main function
    """
    try:
        main(args)
    except Exception as e:
        logging.critical(e, exc_info=True)

