#!/usr/bin/python3
import argparse
import logging
import configparser
import socket
import sys, os
from pycomfoconnect import ComfoConnect
from pycomfoconnect import Bridge
from pycomfoconnect import SENSOR_TEMPERATURE_SUPPLY
from pycomfoconnect import SENSOR_TEMPERATURE_EXHAUST
from pycomfoconnect import SENSOR_TEMPERATURE_EXTRACT
from pycomfoconnect import SENSOR_TEMPERATURE_OUTDOOR
from pycomfoconnect import SENSOR_BYPASS_STATE
from pycomfoconnect import SENSOR_FAN_SPEED_MODE
from pycomfoconnect import SENSOR_OPERATING_MODE
from pycomfoconnect import SENSOR_OPERATING_MODE_BIS
from pycomfoconnect import CMD_FAN_MODE_BOOST_START
#from pycomfoconnect import zehnder_pb2
from time import sleep


# _______________________________________________________________________________________

def sendudp(data, destip, destport):
    # start a new connection udp connection
    connection = socket.socket(socket.AF_INET,     # Internet
                               socket.SOCK_DGRAM)  # UDP

    # send udp datagram
    #res = connection.sendto(data.encode(), (destip, destport))
    res = connection.sendto(data.encode(), (destip, destport))

    # close udp connection
    connection.close()

    # check if all bytes in resultstr were sent
    if res != data.encode().__len__():
        logging.error("Sent bytes do not match - expected {0} : got {1}".format(data.__len__(), res))
        logging.critical("Packet-Payload {0}".format(data))
        sys.exit(-1)

# _______________________________________________________________________________________

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
    
    data = "{0}={1}".format(var,value)
    sendudp(data, miniserverIP, statusPort)
    
    print("CALLBACK: %s = %s" % (var, value))


def main(args):

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
    pin = pluginconfig.get('ZehnderCtrl', 'zehnderPIN')
    zehnderIP = pluginconfig.get('ZehnderCtrl', 'zehnderIP')
    pluginEnabled = pluginconfig.get('ZehnderCtrl', 'enabled')
    
    global statusPort
    statusPort = int(pluginconfig.get('ZehnderCtrl', 'statusPort'))
    global miniserverIP 
    miniserverIP = pluginconfig.get('ZehnderCtrl', 'miniserverIP')
    
    # Discover the bridge
    bridge = bridge_discovery(zehnderIP)

    ## Setup a Comfoconnect session  ###################################################################################

    comfoconnect = ComfoConnect(bridge, local_uuid, local_name, pin)
    comfoconnect.callback_sensor = callback_sensor

    try:
        # Connect to the bridge
        # comfoconnect.connect(False)  # Don't disconnect existing clients.
        comfoconnect.connect(True)  # Disconnect existing clients.

    except Exception as e:
        print('ERROR: %s' % e)
        exit(1)

    ## Register sensors ################################################################################################

    # comfoconnect.register_sensor(SENSOR_FAN_NEXT_CHANGE)  # General: Countdown until next fan speed change
    comfoconnect.register_sensor(SENSOR_FAN_SPEED_MODE)  # Fans: Fan speed setting (65)
    # comfoconnect.register_sensor(SENSOR_FAN_SUPPLY_DUTY)  # Fans: Supply fan duty
    # comfoconnect.register_sensor(SENSOR_FAN_EXHAUST_DUTY)  # Fans: Exhaust fan duty
    # comfoconnect.register_sensor(SENSOR_FAN_SUPPLY_FLOW)  # Fans: Supply fan flow
    # comfoconnect.register_sensor(SENSOR_FAN_EXHAUST_FLOW)  # Fans: Exhaust fan flow
    # comfoconnect.register_sensor(SENSOR_FAN_SUPPLY_SPEED)  # Fans: Supply fan speed
    # comfoconnect.register_sensor(SENSOR_FAN_EXHAUST_SPEED)  # Fans: Exhaust fan speed
    # comfoconnect.register_sensor(SENSOR_POWER_CURRENT)  # Power Consumption: Current Ventilation
    # comfoconnect.register_sensor(SENSOR_POWER_TOTAL_YEAR)  # Power Consumption: Total year-to-date
    # comfoconnect.register_sensor(SENSOR_POWER_TOTAL)  # Power Consumption: Total from start
    # comfoconnect.register_sensor(SENSOR_DAYS_TO_REPLACE_FILTER)  # Days left before filters must be replaced
    # comfoconnect.register_sensor(SENSOR_AVOIDED_HEATING_CURRENT)  # Avoided Heating: Avoided actual
    # comfoconnect.register_sensor(SENSOR_AVOIDED_HEATING_TOTAL_YEAR)  # Avoided Heating: Avoided year-to-date
    # comfoconnect.register_sensor(SENSOR_AVOIDED_HEATING_TOTAL)  # Avoided Heating: Avoided total
    #comfoconnect.register_sensor(SENSOR_TEMPERATURE_SUPPLY)  # Temperature & Humidity: Supply Air (temperature)
    #comfoconnect.register_sensor(SENSOR_TEMPERATURE_EXTRACT)  # Temperature & Humidity: Extract Air (temperature)
    #comfoconnect.register_sensor(SENSOR_TEMPERATURE_EXHAUST)  # Temperature & Humidity: Exhaust Air (temperature)
    #comfoconnect.register_sensor(SENSOR_TEMPERATURE_OUTDOOR)  # Temperature & Humidity: Outdoor Air (temperature)
    #comfoconnect.register_sensor(SENSOR_HUMIDITY_SUPPLY)  # Temperature & Humidity: Supply Air (temperature)
    #comfoconnect.register_sensor(SENSOR_HUMIDITY_EXTRACT)  # Temperature & Humidity: Extract Air (temperature)
    #comfoconnect.register_sensor(SENSOR_HUMIDITY_EXHAUST)  # Temperature & Humidity: Exhaust Air (temperature)
    #comfoconnect.register_sensor(SENSOR_HUMIDITY_OUTDOOR)  # Temperature & Humidity: Outdoor Air (temperature)
    #comfoconnect.register_sensor(SENSOR_BYPASS_STATE)  # Bypass state
    #comfoconnect.register_sensor(SENSOR_OPERATING_MODE)  # Operating mode
    #comfoconnect.register_sensor(SENSOR_OPERATING_MODE_BIS)  # Operating mode (bis)

    # comfoconnect.register_sensor(16) # 1
    # comfoconnect.register_sensor(33) # 1
    # comfoconnect.register_sensor(37) # 0
    # comfoconnect.register_sensor(53) # -1
    # comfoconnect.register_sensor(66) # 0
    # comfoconnect.register_sensor(67) # 0
    # comfoconnect.register_sensor(70) # 0
    # comfoconnect.register_sensor(71) # 0
    # comfoconnect.register_sensor(82) # ffffffff
    # comfoconnect.register_sensor(85) # ffffffff
    # comfoconnect.register_sensor(86) # ffffffff
    # comfoconnect.register_sensor(87) # ffffffff
    # comfoconnect.register_sensor(144) # 0
    # comfoconnect.register_sensor(145) # 0
    # comfoconnect.register_sensor(146) # 0
    # comfoconnect.register_sensor(176) # 0
    # comfoconnect.register_sensor(208) # 0
    # comfoconnect.register_sensor(210) # 0
    # comfoconnect.register_sensor(211) # 0
    # comfoconnect.register_sensor(212) # 228
    # comfoconnect.register_sensor(216) # 0
    # comfoconnect.register_sensor(217) # 28
    # comfoconnect.register_sensor(218) # 28
    # comfoconnect.register_sensor(219) # 0
    # comfoconnect.register_sensor(224) # 3
    # comfoconnect.register_sensor(225) # 1
    # comfoconnect.register_sensor(226) # 100
    # comfoconnect.register_sensor(228) # 0
    # comfoconnect.register_sensor(321) # 15
    # comfoconnect.register_sensor(325) # 1
    # comfoconnect.register_sensor(337) #
    # comfoconnect.register_sensor(338) # 00000000
    # comfoconnect.register_sensor(341) # 00000000
    # comfoconnect.register_sensor(369) # 0
    # comfoconnect.register_sensor(370) # 0
    # comfoconnect.register_sensor(371) # 0
    # comfoconnect.register_sensor(372) # 0
    # comfoconnect.register_sensor(384) # 0
    # comfoconnect.register_sensor(386) # 0
    # comfoconnect.register_sensor(400) # 0
    # comfoconnect.register_sensor(401) # 0
    # comfoconnect.register_sensor(402) # 0
    # comfoconnect.register_sensor(416) # -400
    # comfoconnect.register_sensor(417) # 100
    # comfoconnect.register_sensor(418) # 0
    # comfoconnect.register_sensor(419) # 0

    ## Execute functions ###############################################################################################

    # ListRegisteredApps
    # for app in comfoconnect.cmd_list_registered_apps():
    #     print('%s: %s' % (app['uuid'].hex(), app['devicename']))

    # DeregisterApp
    # comfoconnect.cmd_deregister_app(bytes.fromhex('00000000000000000000000000000001'))

    # VersionRequest
    version = comfoconnect.cmd_version_request()
    print(version)

    # TimeRequest
    # timeinfo = comfoconnect.cmd_time_request()
    # print(timeinfo)

    ## Executing functions #############################################################################################

    # comfoconnect.cmd_rmi_request(CMD_FAN_MODE_AWAY)  # Go to away mode
    # comfoconnect.cmd_rmi_request(CMD_FAN_MODE_LOW)  # Set fan speed to 1
    # comfoconnect.cmd_rmi_request(CMD_FAN_MODE_MEDIUM)  # Set fan speed to 2

    # comfoconnect.cmd_rmi_request(CMD_FAN_MODE_HIGH)  # Set fan speed to 3

    ## Closing the session #############################################################################################

    print('Disconnecting...')
    comfoconnect.disconnect()

# _______________________________________________________________________________________

class Config:
  __loxberry = {
    "LBSCONFIG": os.getenv("LBSCONFIG", os.getcwd()),
  }

  @staticmethod
  def Loxberry(name):
    return Config.__loxberry[name]

# _______________________________________________________________________________________

# parse args and call main function
print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))

if __name__ == "__main__":
    """
    Parse commandline arguments
    """
    parser = argparse.ArgumentParser(description="Loxberry ZehnderCtrl Plugin.")
    
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

