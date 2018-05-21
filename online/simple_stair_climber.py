
"""
Stair Traversal Program

Designed for EEEI stair

Starting point in the center of corridor and stair floor

"""



import logging
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander_edited import MotionCommander

URI = 'radio://0/70/2M'
HEIGHT_MIN = 0.125
HEIGHT_MAX = 0.6

APPEND_LIMIT = 5

TARGET_SIZE = 0.5 #meters per movement
Proportion = 1.2 / 1.5	#real output / target output
MOVE_SIZE =  TARGET_SIZE  / Proportion #more accurate meters per movemet

MOVE_SIZE = 0.7	# comment out to do accurate movement vs predefined intervals


TURN_SIZE =  45 #est degs/sec
RISE_SIZE = 0.05 #m
TURN_RADIUS = 0.3 #m

MOVE_SPEED = 0.35
#0.25, 2 stair movements per charge
#0.5 should be faster but scary

#vectors

height = 0.4
fw = 0
left = 0
angle = 0

will_takeoff = 1
launch_type = 1
#1 for original motion commander
#2 for custom launch version

commandLookup = ["hovering", "forward", "reverse", "left", "right", "yaw left", "yaw right", "ascending", "descending"]

# go up stairs
commands = [0,1,1,1,1,1,1,10]#,7,7,7,7,7,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,90,0,1,1,1,1,1,0,90,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,10]

#go down stairs
#commands = [0,1,107,7,7,7,7,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,270,0,1,1,1,1,1,0,270,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,10]


#0 = stall
#1 = fw
#2 = rv
#3 = left
#4 = right
#5 = yaw left
#6 = yaw right
#7 = add height
#8 = decrease height
#9 = STOP Program
#10 = Land and STOP

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

try:
	if __name__ == '__main__':
		# Initialize the low-level drivers (don't list the debug drivers)
		cflib.crtp.init_drivers(enable_debug_driver=False)
		print(launch_type)
		print(will_takeoff)

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
		#++++++++++++++++++++++++++++++++++++++++++
				appends = 0;
				try:
					while len(commands) >= 0:
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
