import socket, select, string, sys
import cflib.drivers.crazyradio as crazyradio
from time import sleep

import logging
import time
import threading

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander_edited import MotionCommander

from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger

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

commandLookup = ["hovering", "forward", "reverse", "left", "right", "yaw left", "yaw right", "ascending", "descending"]

#commands = [0,360,10]
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


class commander(threading.Thread):

    #stopper = None

    def __init__(self):
        threading.Thread.__init__(self)
        self.running = 1
    def run(self):
        global scf
        global commands
        global commander_start
        global done
        global commander_busy

        # dead reckoning location
        global dr_x
        global dr_y
        global dr_z

        # +x = 0, +y = 1, -x = 2, -y = 3
        global orientation

        # flag if station is connected to drone
        global connected

        commands = []

        while self.running == True:
            print("Thread start")
            # Initialize the low-level drivers (don't list the debug drivers)
            cflib.crtp.init_drivers(enable_debug_driver=False)
            print(launch_type)
            print(will_takeoff)

            with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
                commander_start = 1
                with MotionCommander(scf,default_height= 0.5,will_takeoff = will_takeoff, launch_type=launch_type,minimum_height = HEIGHT_MIN) as mc:
                    cf = mc._cf
            #++++++++++++++++++++++++++++++++++++++++++ Launch Drone
            #        print("---RISING!---")
            #++++++++++++++++++++++++++++++++++++++++++ Launch Drone
                    #mc._is_flying = True # USELESS FOR WITH STATTEMENT
            #++++++++++++++++++++++++++++++++++++++++++

                    mc.stop()
                    print("Starting Sequence")
            #++++++++++++++++++++++++++++++++++++++++++
                    appends = 0;
                    try:
                        while len(commands) >= 0:
                            #if len(commands) == 0:
                                #appends += 1
                                #if appends < APPEND_LIMIT:
                                #    commands.append(0)  #STALL NUMBER
                                #else:
                                #    commands.append(10)  #KILL NUMBER
                            start_time = time.time()
                            while len(commands) == 0:
                                mc.stop()
                                time.sleep(0.1)
                                elapsed_time = time.time() - start_time
                                print("Time: %f" % elapsed_time)
                                if (elapsed_time < MAX_STALL_TIME):
                                    pass
                                else:
                                    commands.append(10)
                                    break

                            if commands[0] == 0:
                                mc.stop()
                                time.sleep(1)


                            elif commands[0] == 1:
                                mc.forward(MOVE_SIZE, velocity=MOVE_SPEED)
                                #print ("fw")
                                if (orientation == 0):
                                    dr_x += 0.5
                                elif (orientation == 1):
                                    dr_y += 0.5
                                elif (orientation == 2):
                                    dr_x -= 0.5
                                elif (orientation == 3):
                                    dr_y -= 0.5

                            elif commands[0] == 2:
                                mc.back(MOVE_SIZE, velocity=MOVE_SPEED)
                                #print ("reverse")
                                if (orientation == 0):
                                    dr_x -= 0.5
                                elif (orientation == 1):
                                    dr_y -= 0.5
                                elif (orientation == 2):
                                    dr_x += 0.5
                                elif (orientation == 3):
                                    dr_y += 0.5


                            elif commands[0] == 3:
                                mc.left(MOVE_SIZE, velocity=MOVE_SPEED)
                                #print ("left")
                                if (orientation == 0):
                                    dr_y += 0.5
                                elif (orientation == 1):
                                    dr_x -= 0.5
                                elif (orientation == 2):
                                    dr_y -= 0.5
                                elif (orientation == 3):
                                    dr_x += 0.5
                                #mc.turn_left(TURN_SIZE)

                            elif commands[0] == 4:
                                mc.right(MOVE_SIZE, velocity=MOVE_SPEED)
                                #print ("right")
                                if (orientation == 0):
                                    dr_y -= 0.5
                                elif (orientation == 1):
                                    dr_x += 0.5
                                elif (orientation == 2):
                                    dr_y += 0.5
                                elif (orientation == 3):
                                    dr_x -= 0.5
                                #mc.turn_right(TURN_SIZE)


                            elif commands[0] == 5:
                                mc.turn_left(TURN_SIZE)
                                mc.turn_left(TURN_SIZE)
                                #print ("yaw left")
                            elif commands[0] == 6:
                                mc.turn_right(TURN_SIZE)
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

                            elif commands[0] == 10:
                                #++++++++++++++++++++++++++++++++++++++++++ Landing Drone=
                                print("!!!-Starting Landing Sequence-!!!")
                                mc.land2()
                                print ("hello")
                                done = 1
                                commander_busy = 0
                                break

                            elif commands[0] == 360:
                                mc.circle_left(0.3,velocity = MOVE_SPEED,angle_degrees = 720)
                                mc.circle_right(0.3,velocity = MOVE_SPEED,angle_degrees = 720)

                            time.sleep(0.1)
                            mc.stop()
                            time.sleep(0.5)

                            #print (commands)
                            if commands[0] > 0 and commands[0] < 9:
                                appends = 0

                            print ("COM: " + str(commandLookup[commands[0]]) + ".\t\t" + str(len(commands) - 2) + " commands left before landing.")


                            commander_busy = 0
                            commands.pop(0)
                    except KeyboardInterrupt:
                        print("---KILLSWITCH ACTIVATED---")
                        print("---EMERGENCY LANDING IMMINENT---")

            #++++++++++++++++++++++++++++++++++++++++++

                    print("Sequence Finished")

            #++++++++++++++++++++++++++++++++++++++++++

                    print("DONE\nNow closing")

                if done == 1:
                    self.running = False

            print("lalala")
            scf.close_link()
            print(scf.is_link_open())
            print("haha")
            time.sleep(0)
    def kill(self):
        self.running = 0
        #mc.land2()

def get_rssi(sock, station_no):

    #initializing crazyradio
    cradio = crazyradio.Crazyradio()
    cradio.set_data_rate(cradio.DR_2MPS)
    cradio.set_channel(70)

    PACKETS_COUNT = 50 # number if packets to send to check whether a drone is present

    count = 0
    rss = 0
    total = 0

    while count < PACKETS_COUNT:
        pk = cradio.send_packet([0xff, ])

        if pk.ack and len(pk.data) > 2 and \
            pk.data[0] & 0xf3 == 0xf3 and pk.data[1] == 0x01:
            count += 1
            rss = pk.data[2]
            total += 1
        else:
            count += 1

    drone_present = 0

    #check if there is a drone present
    if total > 1:
        drone_present = 1
        #print("Drone detected")
    else:
        drone_present = 0
        #print("No drone")

    count = 0
    rss = 0
    x = 20 # number of rss readings to average

    #get x no. of RSS then average
    if drone_present:
        while count < x:
            pk = cradio.send_packet([0xff, ])

            if pk.ack and len(pk.data) > 2 and \
                pk.data[0] & 0xf3 == 0xf3 and pk.data[1] == 0x01:

                count += 1
                rss += pk.data[2]

        rss = rss / x
        rss = int(rss)
    else:
        rss = 10000

    #closing radio
    cradio.close()
    #display RSS reading
    print("RSSI: %d" % rss)
    time.sleep(0.2)
    return rss

def get_rssi_connected():
    global scf

    log_rssi = LogConfig(name='RSSI', period_in_ms=10)
    log_rssi.add_variable('radio.rssi', 'float')

    with SyncLogger(scf, log_rssi) as logger:
        for log_entry in logger:
            print ("Logging RSS")
            timestamp = log_entry[0]
            data = log_entry[1]
            logconf_name = log_entry[2]

            print("RSSI: %d" % data["radio.rssi"])
            return(data["radio.rssi"])

#main function
if __name__ == "__main__":

    global commander_start
    global done
    global commander_busy

    # dead reckoning location
    global dr_x
    global dr_y
    global dr_z

    # +x = 0, +y = 1, -x = 2, -y = 3
    global orientation

    # flag if station is connected to drone
    global connected

    # list of commands for the commander
    global commands

    commander_start = 0 # motion commander started, station connected to drone
    done = 0 # whole program is done
    commander_busy = 0 # motion commander is still executing the command
    connected = 0 # flag if station is connected to drone

    orientation = 1 # default orientation is +y

    commander_thread = commander()

    if(len(sys.argv) < 3) :
        print ('Usage : python3 filename hostname port')
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])

    station_no = int(input("Station No: "))
    #host = raw_input('Enter IP address: ')
    #port = int(raw_input('Enter port number: '))

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print ('Unable to connect')
        sys.exit()

    print ('Connected to remote host. Start sending messages')

    try:
        while 1:
            #socket_list = [sys.stdin, s]
            socket_list = [s]

            # Get the list sockets which are readable
            read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

            for sock in read_sockets:
                #incoming message from remote server
                if sock == s:
                    rcv_data = sock.recv(4096)
                    data = rcv_data.decode('ascii')
                    print(data)
                    if not data :
                        print ('\nDisconnected from chat server 1')
                        commands.append(10)
                        commander_thread.kill()
                        commander_thread.join()
                        sys.exit()
                    else :
                        if " " in data:
                            parsed_data = data.split(" ")

                            # will only go here after start
                            # will only go here to look for station to connect to
                            if parsed_data[0] == "get_rssi":

                                dr_x = int(parsed_data[1])
                                dr_y = int(parsed_data[2])
                                dr_z = int(parsed_data[3])

                                orientation = 1

                                rss = get_rssi(sock, station_no)

                                reply = "rss " + str(station_no) + " " + str(rss)
                                s.send(reply.encode('ascii'))

                            elif parsed_data[0] == "connect":
                                if int(parsed_data[1]) == station_no:

                                    commander_thread.start()

                                    while commander_start != 1:
                                        #print("Starting...")
                                        pass

                                    connected = 1
                                    reply = "Connected to Station " + str(station_no)
                                    s.send(reply.encode('ascii'))

                            elif parsed_data[0] == "command":
                                if connected == 1:
                                    commander_busy = 1
                                    commands.append(int(parsed_data[1]))
                                    print(commands)

                                while commander_busy == 1:
                                    pass

                                reply = "Command done"
                                #reply = "Command sent"
                                s.send(reply.encode('ascii'))

                            else:
                                print (data)

                        else:
                            if data == "get_rssi":

                                #rss = get_rssi(sock, cradio, station_no)
                                if connected == 0:
                                    rss = get_rssi(sock, station_no)
                                else:
                                    rss = int(get_rssi_connected())

                                reply = "rss " + str(station_no) + " " + str(rss)
                                s.send(reply.encode('ascii'))

                            elif data == "done":
                                done = 1

                            elif data == "get_dr_loc":
                                reply = "dr_loc " + str(dr_x) + " " + str(dr_y) + " " + str(dr_z) + " " + str(orientation)
                                print(reply)
                                s.send(reply.encode('ascii'))

                            else:
                                print (data)

                #user entered a message
                else :
                    msg = input("")
                    s.send(msg.encode('ascii'))
                    if msg == "/quit\n":
                        print ('Disconnecting from server...')
                        break

    except KeyboardInterrupt:
        msg = '/quit\n'
        s.send(msg.encode('ascii'))
        print ('Disconnecting from server...')
        print ('\nDisconnected from chat server 2')
        s.close()
        commands.append(10)
        commander_thread.kill()
        commander_thread.join()
