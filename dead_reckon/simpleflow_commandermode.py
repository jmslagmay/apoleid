
"""
Simple example that connects to the crazyflie at `URI` and runs a figure 8
sequence. This script requires some kind of location system, it has been
tested with (and designed for) the flow deck.

Change the URI variable to your Crazyflie configuration.
"""



import logging
import time
import threading

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander

from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger

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

commandLookup = ["stabilizing...", "forward", "reverse", "left", "right", "yaw left", "yaw right", "ascending", "descending"]

commands = [0,7,9]
#0 = stall
#1 = fw
#2 = rv
#3 = left
#4 = right
#5 = yaw left
#6 = yaw right
#7 = add height
#8 = decrease height
#9 = kill

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

try:

    class get_rss(threading.Thread):

        def __init__(self, scf):
            threading.Thread.__init__(self)
            self.scf = scf
            self.running = 1
        def run(self):
            #cradio = crazyradio.Crazyradio()
            print ("hi")
            #print (cradio)
            #cradio.set_data_rate(cradio.DR_2MPS)
            #cradio.set_channel(70)
            print ("Thread start")

            log_rssi = LogConfig(name='RSSI', period_in_ms=1000)
            log_rssi.add_variable('radio.rssi', 'float')

            while self.running == True:

                with SyncLogger(scf, log_rssi) as logger:
                endTime = time.time() + 10

                for log_entry in logger:
                    timestamp = log_entry[0]
                    data = log_entry[1]
                    logconf_name = log_entry[2]

                    #print('[%d][%s]: %s' % (timestamp, logconf_name, data))
                    print(data["radio.rssi"])

                    if time.time() > endTime:
                        break
                
                time.sleep(0)
        def kill(self):
            self.running = 0

    if __name__ == '__main__':
        # Initialize the low-level drivers (don't list the debug drivers)
        cflib.crtp.init_drivers(enable_debug_driver=False)

        

        with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:

            print (scf)
            g_rss = get_rss(scf)
            g_rss.start()

            with MotionCommander(scf) as mc:
        #++++++++++++++++++++++++++++++++++++++++++ Launch Drone
                time.sleep(1)
                mc.up(0.5)
                time.sleep(1)

                print("Launch DONE. Height achieved: " + str(height))

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
                            else:
                                print("Heigh MAX Reached")
                            #print("Ascend")
                            
                        elif commands[0] == 8:
                            if (height - RISE_SIZE) >= 0.225:
                                mc.down(RISE_SIZE) 
                            else:
                                print("Heigh MAX Reached")
                            #print("Descend")
                            
                        elif commands[0] == 9:
                            mc.stop()
                            break
                            
                            
                        elif commands[0] == 360:
                            mc.circle_left(0.5,velocity = MOVE_SPEED,angle_degrees = 720)
                        time.sleep(0.1)
                        mc.stop()

                        #print (commands)
                        print ("COM: " + str(commandLookup[commands[0]]) + ". " + str(len(commands) - 2) + " commands left before landing.")



                        commands.pop(0)
                except KeyboardInterrupt:
                    print("---KILLSWITCH ACTIVATED---")
                    print("---EMERGENCY LANDING IMMINENT---")
                    
        #++++++++++++++++++++++++++++++++++++++++++

                print("Sequence Finished")
        #++++++++++++++++++++++++++++++++++++++++++ Landing Drone

                print("!!!-Starting Landing Sequence-!!!")
                mc.stop()
                    
        #++++++++++++++++++++++++++++++++++++++++++
                
                print("DONE\nNow closing")

            
finally:
    print("Finally, we end.")
