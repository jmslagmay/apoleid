import socket, select, string, sys
import cflib.drivers.crazyradio as crazyradio
from time import sleep

#def get_rssi(sock, cradio, station_no):
def get_rssi(sock, station_no):


    cradio = crazyradio.Crazyradio()
    cradio.set_data_rate(cradio.DR_2MPS)
    cradio.set_channel(70)

    count = 0
    #delay = (float(station_no) - 1) / 10
    #delay = (float(station_no) - 1)
    delay = (station_no - 1) * 2
    #addr = 0xff - station_no - 1
    #print (delay)
    #print (addr)
    rss = 0
    total = 0

    #cradio = crazyradio.Crazyradio()
    #cradio.set_data_rate(cradio.DR_2MPS)
    #cradio.set_channel(70)


    #RSS_list = []
    sleep(delay)

    while count < 100:

        pk = cradio.send_packet([0xff, ])

        if pk.ack and len(pk.data) > 2 and \
            pk.data[0] & 0xf3 == 0xf3 and pk.data[1] == 0x01:

            #print("RSSI: -{}dBm".format(pk.data[2]))
            #print ("RSSI: %d" % pk.data[2])
            count += 1
            rss = pk.data[2]
            #RSS_list.append(rss)
            #print("hello")
            total += 1

        else:
            #print("No RSS")
            count += 1
            #print("hi")
            #rss = 10000



    drone = 0

    #check if there is a drone present
    if total > 1:
        drone = 1
        print("Drone detected")
    else:
        drone = 0
        print("No drone")

    count = 0
    rss = 0
    x = 20

    #get x no. of RSS then average
    if drone:
        #for i in range (0, len(RSS_list)):
        #    rss_sum += RSS_list[i]

        #rss = int(rss_sum / len(RSS_list))

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


    cradio.close()
    print("RSSI: %d" % rss)
    return rss



#main function
if __name__ == "__main__":

    if(len(sys.argv) < 3) :
        print ('Usage : python3 filename hostname port')
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])

    station_no = int(input("Station No: "))
    #channel = 70 + station_no



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
            socket_list = [s]

            # Get the list sockets which are readable
            read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

            for sock in read_sockets:
                #incoming message from remote server
                if sock == s:
                    rcv_data = sock.recv(4096)
                    data = rcv_data.decode('ascii')
                    if not data :
                        print ('\nDisconnected from chat server')
                        sys.exit()
                    else :
                        #sys.stdout.write(data)
                        #print(data)

                        if " " in data:
                            parsed_data = data.split(" ")

                            if parsed_data[0] == "get_rssi":

                                #print ("GET RSSI!!!!!!!!!!!")
                                #print (str(station_no) + " rss " + "35")

                                #cradio = crazyradio.Crazyradio()
                                #cradio.set_data_rate(cradio.DR_2MPS)
                                #cradio.set_channel(70)

                                #rss = get_rssi(sock, cradio, station_no)

                                rss = get_rssi(sock, station_no)

                                reply = "rss " + str(station_no) + " " + str(rss)
                                s.send(reply.encode('ascii'))

                            else:

                                print (data)

                        else:
                            if data == "get_rssi":

                                #cradio = crazyradio.Crazyradio()
                                #cradio.set_data_rate(cradio.DR_2MPS)
                                #cradio.set_channel(70)

                                #rss = get_rssi(sock, cradio, station_no)

                                rss = get_rssi(sock, station_no)

                                reply = "rss " + str(station_no) + " " + str(rss)
                                s.send(reply.encode('ascii'))

                            else:

                                print (data)

                #user entered a message
                else :
                    #msg = sys.stdin.readline()
                    msg = input("")
                    #print (len(msg))
                    s.send(msg.encode('ascii'))
                    if msg == "/quit\n":
                        print ('Disconnecting from server...')
                        break

    except KeyboardInterrupt:
        msg = '/quit\n'
        s.send(msg.encode('ascii'))
        print ('Disconnecting from server...')
        print ('\nDisconnected from chat server')
        s.close()
