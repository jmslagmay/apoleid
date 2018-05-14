import logging
import time
from threading import Timer

import cflib.crtp  # noqa
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig

# imports already in the integrated code

from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander_edited import MotionCommander

# common imports end here

logging.basicConfig(level=logging.ERROR)
floatzero = float(0)
status_check_duration = 20

ir_sum = 0
prev_ir_sum = 0
battery_sum = 0

IR_ALARM_VAL = 1300 #1.3 volts
MAX_BATTERY = 4127
LOW_BATTERY = 3650 # PRACTICAL LOW BATTERY
#LOW_BATTERY = 3570 #ACTUAL CORRECT VALUE NOT FLYING 2.820 FOR flying
LOWEST_BATTERY = 2330
percentage = 10

state = 0
alignment = 0

# Variables already in the integrated code

URI = 'radio://0/70/2M'
HEIGHT_MIN = 0.125
HEIGHT_MAX = 0.6

APPEND_LIMIT = 5

TARGET_SIZE = 0.5 #meters per movement
Proportion = 1.2 / 1.5    #real output / target output
MOVE_SIZE =  TARGET_SIZE  / Proportion #more accurate meters per movemet

MOVE_SIZE = 0.5    # comment out to do accurate movement vs predefined intervals
TURN_SIZE =  45 #est degs/sec
RISE_SIZE = 0.05 #m

MOVE_SPEED = 0.25
MAX_STALL_TIME = 3

#vectors

height = 0.4
fw = 0
left = 0
angle = 0

will_takeoff = 1
launch_type = 1
#1 for original motion commander
#2 for custom launch version

# Common variables end here

class LoggingExample:
    """
    Simple logging example class that logs the Stabilizer from a supplied
    link uri and disconnects after 5s.
    """

    def __init__(self, link_uri):
        """ Initialize and run the example with the specified link_uri """

        self._cf = Crazyflie(rw_cache='./cache')

        # Connect some callbacks from the Crazyflie API
        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        print('Connecting to %s' % link_uri)

        # Try to connect to the Crazyflie
        self._cf.open_link(link_uri)

        # Variable used to keep main loop occupied until disconnect
        self.is_connected = True

    def _connected(self, link_uri):
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""
        print('Connected to %s' % link_uri)

        # The definition of the logconfig can be made before connecting
        self._lg_bat = LogConfig(name='Battery stats', period_in_ms=10)
        self._lg_bat.add_variable('pm.vbat', 'float')
        self._lg_bat.add_variable('forwardRange.forwardRange', 'float')

        # Adding the configuration cannot be done until a Crazyflie is
        # connected, since we need to check that the variables we
        # would like to log are in the TOC.
        try:
            self._cf.log.add_config(self._lg_bat)
            # This callback will receive the data
            self._lg_bat.data_received_cb.add_callback(self._stab_log_data)
            # This callback will be called on errors
            self._lg_bat.error_cb.add_callback(self._stab_log_error)
            # Start the logging
            self._lg_bat.start()
        except KeyError as e:
            print('Could not start log configuration,'
                  '{} not found in TOC'.format(str(e)))
        except AttributeError:
            print('Could not add Stabilizer log config, bad configuration.')

        # Start a timer to disconnect in 10s
        t = Timer(status_check_duration, self._cf.close_link)
        t.start()

    def _stab_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print('Error when logging %s: %s' % (logconf.name, msg))

    # The lines below detail the start of logging for Battery and IR
	def _stab_log_data(self, timestamp, data, logconf):
        """Callback froma the log API when data arrives"""
        print('[%d][%s]: %s' % (timestamp, logconf.name, data))
        bat_data = data ['pm.vbat']
        bat_data = float(bat_data) * float(1000)
        bat_data = int(bat_data)

        self._battery_voltage(floatvolt = bat_data)

        ir_data = data ['forwardRange.forwardRange']
        ir_data = float(ir_data) * float(1000)
        ir_data = int(ir_data)

        obstacle_status = self._ir_check(ir_data = ir_data)
	# Getting Log Data ends here

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the speficied address)"""
        print('Connection to %s failed: %s' % (link_uri, msg))
        self.is_connected = False

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print('Connection to %s lost: %s' % (link_uri, msg))

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print('Disconnected from %s' % link_uri)
        self.is_connected = False

    # Function that tells CrazyFlie 2.0 behavior
	# in the event of an obstacle
	# States described here:
	"""
	11 - 10 - 12
	01 - CF - 02
	
	"""
	def irEvent(state):
		
		# Reference: In case we are going to use the
		# command.insert(0, newCommand)
		
		# Start checking
		# Drone Yaw Left
		mc.turn_left(TURN_SIZE)
		mc.turn_left(TURN_SIZE)
		
		# If clear, move forward then yaw right (State 01)
		if (self._ir_check(ir_data = ir_data) == 0):
			mc.forward(MOVE_SIZE, velocity=MOVE_SPEED)
			# dr_x -= 0.5     !!! DR value - Uncomment this when merging code to integ.
			mc.turn_right(TURN_SIZE)
			mc.turn_right(TURN_SIZE)
			state = 1
		# Else, yaw right (State 00)
			mc.turn_right(TURN_SIZE)
			mc.turn_right(TURN_SIZE)
			state = 0
			
		# If none of that worked, check right side.
		if (state == 0):
			mc.turn_right(TURN_SIZE)
			mc.turn_right(TURN_SIZE)			
		
			# If clear, move forward then yaw left (State 02)
			if (self._ir_check(ir_data = ir_data) == 0):
				mc.forward(MOVE_SIZE, velocity=MOVE_SPEED)
				# dr_x += 0.5     !!! DR value - Uncomment this when merging code to integ.
				mc.turn_left(TURN_SIZE)
				mc.turn_left(TURN_SIZE) # Make it face right
				state = 2
			# Else, yaw left then land
				mc.turn_left(TURN_SIZE)
				mc.turn_left(TURN_SIZE)
				# gonna force the entire sequence to kill everything
				# uncomment when integrating with main code
				# commands.insert(0, 10)
				state = 0
			
		# Keep track of the current grid alignment
		# if it's displaced from the center of the grid
		alignment = state
	
	# Function that determines Battery Percentage
	def _battery_voltage(self, floatvolt = floatzero):
        global battery_sum
        #print('DEBUG: Battery Read in progress')
        if (battery_sum == 0 ):
            battery_sum = floatvolt
        else :
            battery_sum = (battery_sum + floatvolt)/2

        percentage = ((battery_sum - LOW_BATTERY) *100) / (MAX_BATTERY - LOW_BATTERY)
        print('%s Battery = %d\n\n%d %%\n\n' % (floatvolt,battery_sum,percentage))
		
    # Function that determines IR status (Free or Obstructed)
	def _ir_check(self, ir_data = floatzero):
        """
        global ir_sum
        global prev_ir_sum
        prev_ir_sum = ir_sum

        print('IR process')
        if (ir_sum == 0 ):
            ir_sum = ir_data
        else :
            ir_sum = (ir_sum + ir_data)/2

        print('%s and IR = %d' % (ir_data,ir_sum))
        print('%s - %d\n' % (prev_ir_sum,ir_sum))


        if (abs(prev_ir_sum - ir_sum)) >= 1:
            print("%d  =  IR Difference\n\n" % (abs(prev_ir_sum - ir_sum)))
        else:
            print("%d = NO OBSTACLE Detected\n\n" % (abs(prev_ir_sum - ir_sum)))
        """

        global ir_sum

        #print('DEBUG: IR process')
        if (ir_sum == 0 ):
            ir_sum = ir_data
        else :
            ir_sum = (ir_sum + ir_data)/2

        print('%s and IR = %d' % (ir_data,ir_sum))


        if (ir_sum >= IR_ALARM_VAL) or (ir_data >= IR_ALARM_VAL):
            print("%d:sum| IR |value: %d\n STOP\n STOP\n STOP\n STOP" % (ir_sum,ir_data))
			return 1
        else:
            print("%d:sum| IR |value: %d \nCHILL\n" % (ir_sum,ir_data))
			return 0




if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    # Scan for Crazyflies and use the first one found
    print('Scanning interfaces for Crazyflies...')
    #available = cflib.crtp.scan_interfaces()
    print('Crazyflies found:')
    #for i in available:
   #     print(i[0])

    if 1 > 0:
        le = LoggingExample('radio://0/70/2M')
    else:
        print('No Crazyflies found, cannot run example')

    # The Crazyflie lib doesn't contain anything to keep the application alive,
    # so this is where your application should do something. In our case we
    # are just waiting until we are disconnected.
    while le.is_connected:
        time.sleep(1)
