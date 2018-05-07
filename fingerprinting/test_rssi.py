# cflib can be installed via 'pip install cflib'
import cflib.drivers.crazyradio as crazyradio
from time import sleep

cradio = crazyradio.Crazyradio()

# Connection parameter for the CF2
cradio.set_data_rate(cradio.DR_2MPS)
cradio.set_channel(70)

count = 0
total = 0

for _ in range(80):
    pk = cradio.send_packet([0xff, ])
    #print (pk)
    sleep(0.1)
    #print (pk.ack)
    #print (pk.retry)
    #print (pk.data)
    #print ("")
    count += 1
    # Filter for NULL packet that includes a RSSI measurement
    # -> Null packet have a header of 0xF3, with a mask of 0xF3
    # -> RSSI NULL packets have 1 after the header, and the RSSI after
    if pk.ack and len(pk.data) > 2 and \
        pk.data[0] & 0xf3 == 0xf3 and pk.data[1] == 0x01:
        print("RSSI {}: -{}dBm".format(count, pk.data[2]))
        total += 1
    #print (pk.ack)
    #print (pk.data)
print("Total: %d" % total)
cradio.close()
