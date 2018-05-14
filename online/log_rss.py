import logging
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger

logging.basicConfig(level=logging.ERROR)

if __name__=="__main__":

    cflib.crtp.init_drivers(enable_debug_driver=False)
    print('Scanning interfces for Crazyflies...')
    available = cflib.crtp.scan_interfaces()
    print ('Crazyflies found:')
    for i in available:
        print(i[0])

        if len(available) == 0:
            print('No Crazyflies found, cannot run example')
        else:
            #lg_rss = LogConfig('RSSI', period_in_ms=10)
            #lg_rss.add_variable('radio.rssi', 'float')
            lg_stab = LogConfig(name='Stabilizer', period_in_ms=10)
            lg_stab.add_variable('stabilizer.yaw', 'float')

            cf = Crazyflie(rw_cache='./cache')

            with SyncCrazyflie(available[0][0], cf=cf) as scf:
                with SyncLogger(scf, lg_stab) as logger:
                    print (scf)
                    print(logger)
                    endTime = time.time() + 10
                    print("1")
                    for log_entry in logger:
                        print("2")
                        timestamp = log_entry[0]
                        data = log_entry[1]
                        logconf_name = log_entry[2]

                        print('[%d][%s]: %s' % (timestamp, logconf_name, data))

                        if time.time() > endTime:
                            break
