# cflib can be installed via 'pip install cflib'
import cflib.drivers.crazyradio as crazyradio

cradio = crazyradio.Crazyradio()

# Connection parameter for the CF2
cradio.set_data_rate(cradio.DR_2MPS)
cradio.set_channel(70)

x = input("X: ")
y = input("Y: ")
z = input("Z: ")

rssi_sum = 0
count = 0

for _ in range(3):
    pk = cradio.send_packet([0xff, ])

    # Filter for NULL packet that includes a RSSI measurement
    # -> Null packet have a header of 0xF3, with a mask of 0xF3
    # -> RSSI NULL packets have 1 after the header, and the RSSI after
    print (pk.ack)
    print (pk.data)
    print (len(pk.data))
    print (pk.data[0])
    #print (pk.data[1])
    print ("\n")

    if pk.ack and len(pk.data) > 2 and \
        pk.data[0] & 0xf3 == 0xf3 and pk.data[1] == 0x01:
        #print("RSSI: -{}dBm".format(pk.data[2]))
        rssi_sum += pk.data[2]
        count += 1
        print (count)
    

    #print (pk.ack)
    #print (pk.data[2])
    #print("RSSI: -{}dBm".format(pk.data[2]))
print ("Closing...")
cradio.close()

rss = rssi_sum/count
print (rss)

to_db = x + "," + y + "," + z + "," + str(rss)

db = open("rss_db.csv", "a")
db.write(to_db)



