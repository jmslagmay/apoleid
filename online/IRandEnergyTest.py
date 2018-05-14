
"""
Simple example that connects to the crazyflie at `URI` and runs a figure 8
sequence. This script requires some kind of location system, it has been
tested with (and designed for) the flow deck.

Change the URI variable to your Crazyflie configuration.
"""

import logging
import time
from threading import Timer

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander_edited import MotionCommander

from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger

floatzero = float(0)
status_check_duration = 20

ir_avg = 0
battery_avg = 0
ir_data = 0

IR_ALARM_VAL = 1300 #1.3 volts
MAX_BATTERY = 4127
LOW_BATTERY_NOTFLY = 3650 # PRACTICAL LOW BATTERY
LOW_BATTERY_FLY = 3100 # PRACTICAL LOW BATTERY
#LOW_BATTERY = 3570 #ACTUAL CORRECT VALUE NOT FLYING 2.820 FOR flying
LOWEST_BATTERY = 2330
percentage = 10

state = 0
alignment = 0

URI = 'radio://0/70/2M'
HEIGHT_MIN = 0.125
HEIGHT_MAX = 0.6

APPEND_LIMIT = 5

TARGET_SIZE = 0.5
Proportion = 1.2 / 1.5
MOVE_SIZE =  TARGET_SIZE  / Proportion #est m/s

MOVE_SIZE = 0.5
TURN_SIZE =  45 #est degs/sec
RISE_SIZE = 0.05 #m

MOVE_SPEED = 0.25

#vectors

height = 0.4
fw = 0
left = 0
angle = 0

will_takeoff = 1
launch_type = 1

#commandLookup = ["stabilizing...", "forward", "reverse", "left", "right", "yaw left", "yaw right", "ascending", "descending"]

commands = [0,0,1,1,1,1,0,10]
#0 = stall
#1 = fw
#2 = rv
#3 = left
#4 = right
#5 = yaw left
#6 = yaw right
#7 = add height
#8 = decrease height

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

def ir_and_energy():
	global scf
	global ir_data
	# The definition of the logconfig can be made before connecting
	log_irnbat = LogConfig(name='IR and Battery', period_in_ms=10)
	log_irnbat.add_variable('pm.vbat', 'float')
	log_irnbat.add_variable('forwardRange.forwardRange', 'float')

	print("Logging IR and Energy")

	count = 0

	with SyncLogger(scf, log_irnbat) as irnbatlogger:
		for log_entry in irnbatlogger:
			data = log_entry[1]
			#print(data)
			bat_data = data['pm.vbat']
			bat_data = float(bat_data) * float(1000)
			bat_data = int(bat_data)

			battery_voltage(floatvolt = bat_data)

			ir_data = data['forwardRange.forwardRange']
			ir_data = float(ir_data) * float(1000)
			ir_data = int(ir_data)

			ir_process(ir_data = ir_data)
			count = count + 1

			if (count == 5):
				break
# Getting Log Data ends here

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

	#print("Doing IR Event")

	# Start checking
	# Drone Yaw Left
	mc.turn_left(TURN_SIZE)
	mc.turn_left(TURN_SIZE)

	time.sleep(1)

	ir_and_energy() # Get a reading

	# If clear, move forward then yaw right (State 01)
	time.sleep(1)
	if (ir_check(ir_avg, ir_data) == 0):
		print("Left is clear. Moving forward")
		mc.forward(MOVE_SIZE, velocity=MOVE_SPEED)
		# dr_x -= 0.5     !!! DR value - Uncomment this when merging code to integ.
		mc.turn_right(TURN_SIZE)
		time.sleep(0.5)
		mc.turn_right(TURN_SIZE)
		state = 1
	# Else, yaw right (State 00)
	else:
		print("Left is no good. Checking Right")
		mc.turn_right(TURN_SIZE)
		time.sleep(0.5)
		mc.turn_right(TURN_SIZE)
		state = 0

	# If none of that worked, check right side.
	time.sleep(1)

	if (state == 0):
		mc.turn_right(TURN_SIZE)
		time.sleep(0.5)
		mc.turn_right(TURN_SIZE)

		ir_and_energy() # Get a reading
		time.sleep(1)

		# If clear, move forward then yaw left (State 02)
		if (ir_check(ir_avg, ir_data) == 0):
			print("Right is good. Moving forward")
			mc.forward(MOVE_SIZE, velocity=MOVE_SPEED)
			# dr_x += 0.5     !!! DR value - Uncomment this when merging code to integ.
			mc.turn_left(TURN_SIZE)
			time.sleep(0.5)
			mc.turn_left(TURN_SIZE) # Make it face right
			state = 2
		# Else, yaw left then land
		else:
			print("No available paths. Landing now.")
			mc.turn_left(TURN_SIZE)
			time.sleep(0.5)
			mc.turn_left(TURN_SIZE)
			# gonna force the entire sequence to kill everything
			# uncomment when integrating with main code
			# commands.insert(0, 10)
			state = 0

	# Keep track of the current grid alignment
	# if it's displaced from the center of the grid
	alignment = state

# Function that determines Battery Percentage
def battery_voltage(floatvolt = floatzero):
	global battery_avg
	#print('DEBUG: Battery Read in progress')
	if (battery_avg == 0 ):
		battery_avg = floatvolt
	else :
		battery_avg = (battery_avg + floatvolt)/2

	percentage = ((battery_avg - LOW_BATTERY_FLY) *100) / (MAX_BATTERY - LOW_BATTERY_FLY)
	print(str(battery_avg) + " " + str(LOW_BATTERY_FLY))
	print('%s Battery = %d\n\n%d %%\n\n' % (floatvolt,battery_avg,percentage))

# Function that determines IR status (Free or Obstructed)
def ir_process(ir_data = floatzero):
	global ir_avg

	#print('DEBUG: IR process')
	if (ir_avg == 0 ):
		ir_avg = ir_data
	else :
		ir_avg = (ir_avg + ir_data)/2

	print('%s and IR = %d' % (ir_data,ir_avg))


def ir_check(ir_avg, ir_data):
	if (ir_avg >= IR_ALARM_VAL) or (ir_data >= IR_ALARM_VAL):
		print("%d:sum| IR |value: %d\n STOP\n STOP\n STOP\n STOP" % (ir_avg,ir_data))
		return 1
	else:
		print("%d:sum| IR |value: %d \nCHILL\n" % (ir_avg,ir_data))
		return 0

try:
	if __name__ == '__main__':
		# Initialize the low-level drivers (don't list the debug drivers)
		cflib.crtp.init_drivers(enable_debug_driver=False)

		with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
			with MotionCommander(scf,default_height= 0.5,will_takeoff = will_takeoff, launch_type=launch_type,minimum_height = HEIGHT_MIN) as mc:
				cf = mc._cf
		#++++++++++++++++++++++++++++++++++++++++++ Launch Drone
		#		print("---RISING!---")
		#++++++++++++++++++++++++++++++++++++++++++ Launch Drone
				#mc._is_flying = True # USELESS FOR WITH STATTEMENT
		#++++++++++++++++++++++++++++++++++++++++++
				mc.stop()
				print("Starting Sequence")

				#ir_and_energy()

		#++++++++++++++++++++++++++++++++++++++++++
				appends = 0;
				try:
					while len(commands) >= 0:
						ir_and_energy()
						if (ir_check(ir_avg, ir_data)):
							irEvent(0)

						if len(commands) == 0:
							appends += 1
							if appends < APPEND_LIMIT:
								commands.append(0)  #STALL NUMBER
							else:
								commands.append(9)  #KILL NUMBER


						if commands[0] == 0:
							mc.stop()
							time.sleep(1)


						elif commands[0] == 1:
							mc.forward(MOVE_SIZE, velocity=MOVE_SPEED)
							#print ("fw")
						elif commands[0] == 2:
							mc.back(MOVE_SIZE, velocity=MOVE_SPEED)
							#print ("reverse")


						elif commands[0] == 3:
							mc.left(MOVE_SIZE, velocity=MOVE_SPEED)
							#print ("left")
						elif commands[0] == 4:
							mc.right(MOVE_SIZE, velocity=MOVE_SPEED)
							#print ("right")


						elif commands[0] == 5:
							mc.turn_left(TURN_SIZE)
							#print ("yaw left")
						elif commands[0] == 6:
							mc.turn_right(TURN_SIZE)
							#print ("yaw right")


						elif commands[0] == 7:
							if (height + RISE_SIZE) <=HEIGHT_MAX:
								mc.up(RISE_SIZE)
								height += RISE_SIZE
							else:
								print("Heigh MAX Reached")
							#print("Ascend")

						elif commands[0] == 8:
							if (height - RISE_SIZE) >= 0.225:
								mc.down(RISE_SIZE)
								height -= RISE_SIZE
							else:
								print("Heigh MAX Reached")
							#print("Descend")

						elif commands[0] == 9:
							mc.stop()
							break

						elif commands[0] == 10:
							#++++++++++++++++++++++++++++++++++++++++++ Landing Drone=
							print("!!!-Starting Landing Sequence-!!!")
							mc.land2()

							break

						elif commands[0] == 90:
							mc.circle_right(TURN_RADIUS	,velocity = MOVE_SPEED,angle_degrees = 90)

						elif commands[0] == 270:
							mc.circle_left(TURN_RADIUS,velocity = MOVE_SPEED,angle_degrees = 90)


						time.sleep(0.1)
						mc.stop()

						#print (commands)
						if commands[0] > 0 and commands[0]<9:
							appends = 0

						#print ("COM: " + str(commandLookup[commands[0]]) + ".\t\t" + str(len(commands) - 2) + " commands left before landing.")



						commands.pop(0)
				except KeyboardInterrupt:
					print("---KILLSWITCH ACTIVATED---")
					print("---EMERGENCY LANDING IMMINENT---")

		#++++++++++++++++++++++++++++++++++++++++++

				print("Sequence Finished")

		#++++++++++++++++++++++++++++++++++++++++++

				print("DONE\nNow closing")


finally:
	print("Finally, we end.")
