# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2016 Bitcraze AB
#
#  Crazyflie Nano Quadcopter Client
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA  02110-1301, USA.
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
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger

logging.basicConfig(level=logging.ERROR)

URI = 'radio://0/70/2M'

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

class log(threading.Thread):

    #stopper = None

    def __init__(self):
        threading.Thread.__init__(self)
        #self.s_sock = s_sock
#        self.stopper = stopper
        self.running = 1
    def run(self):
        global scf        

        while self.running == True:
        #while not self.stopper.is_set():
            lg_motion = LogConfig(name='Motion', period_in_ms=1000)
            lg_motion.add_variable('motion.deltaX', 'float')
            lg_motion.add_variable('motion.deltaY', 'float')

            #cf = Crazyflie(rw_cache='./cache')
            #with SyncCrazyflie(available[0][0], cf=cf) as scf:
            with SyncLogger(scf, lg_motion) as logger:
                endTime = time.time() + 10

                for log_entry in logger:
                    timestamp = log_entry[0]
                    data = log_entry[1]
                    logconf_name = log_entry[2]

                    print('[%d][%s]: %s' % (timestamp, logconf_name, data))

                    if time.time() > endTime:
                        break

            time.sleep(0)
    def kill(self):
        self.running = 0


if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)

    global scf

    cflib.crtp.init_drivers(enable_debug_driver=False)

    

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        cf = scf.cf

        log_flow = log()
        log_flow.start()

        cf.param.set_value('kalman.resetEstimation', '1')
        time.sleep(0.1)
        cf.param.set_value('kalman.resetEstimation', '0')
        time.sleep(2)

        

        for y in range(10):
            cf.commander.send_hover_setpoint(0, 0, 0, y / 25)
            time.sleep(0.1)

        for _ in range(10):
            cf.commander.send_hover_setpoint(0, 0, 0, 0.2)
            time.sleep(0.1)

        #for _ in range(50):
        #    cf.commander.send_hover_setpoint(0.5, 0, 36 * 2, 0.4)
        #    time.sleep(0.1)

        #for _ in range(50):
        #    cf.commander.send_hover_setpoint(0.5, 0, -36 * 2, 0.4)
        #    time.sleep(0.1)

        #for _ in range(20):
        #    cf.commander.send_hover_setpoint(0, 0, 0, 0.4)
        #    time.sleep(0.1)

        for y in range(10):
            cf.commander.send_hover_setpoint(0, 0, 0, (10 - y) / 25)
            time.sleep(0.1)

        cf.commander.send_stop_setpoint()
