import socket, select, time, sys, threading, signal, math, zmq

commandLookup = ["hover", "forward", "reverse", "left", "right", "yaw left", "yaw right", "ascending", "descending", "stop", "landing", "handoff"]

#Function to broadcast chat messages to all connected clients
def broadcast_data (sock, message):
    #Do not send the message to master socket and the client who has send us the message
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock :
            try :
                socket.send(message.encode('ascii'))
            except :
                # broken socket connection may be, chat client pressed ctrl+c for example
                socket.close()
                CONNECTION_LIST.remove(socket)

class commanding_thread(threading.Thread):

    def __init__(self, s_sock):
        threading.Thread.__init__(self)
        self.s_sock = s_sock
#        self.stopper = stopper
        self.running = 1
    def run(self):
        # --------- FLAGS ----------
        global get_rss_flag

        global op_started
        global cycle_on
        global command_done
        global get_dr_flag
        global connected
        global get_batt_flag
        #global connecting_flag

        # command received from Unity
        global command

        # actual location
        global current_x
        global current_y
        global current_z

        global batt

        room_lookup = {'209': [0, -1, 0], '210': [0, -1, 0], '207': [0, 0, 0], '208': [0, 1, 0], '206': [0, 7, 0], '204': [0, 9, 0], '205': [0, 12, 0], '201': [0, 19, 0], '203': [0, 19, 0], '202': [0, 21, 0], '220': [-20, 24, 0], '225': [-46, 24, 0], '226': [-48, 30, 0], '227': [-48, 28, 0], '228': [-48, 21, 0], '229': [-48, 15, 0]}
        #print(room_lookup)
        #print(room_lookup['209'][1])

        count = 0
        while self.running:
            text = ""

            if op_started == 0 and count == 0:
                count += 1
                #print (count)
                text = input('')

                #broadcast_data(self.s_sock, text)
                #time.sleep(0.1)
                if " " in text:
                    #text = ""
                    split_text = text.split(" ")

                    if split_text[0] == "start":
                        print ("\t\t\t\tSTATUS: Starting drone operation...")
                        #text = ""
                        text2 = "get_rssi " + str(room_lookup[split_text[1]][0]) + " " + str(room_lookup[split_text[1]][1]) + " " + str(room_lookup[split_text[1]][2])

                        #print(text2)
                        time.sleep(0.1)
                        #print(text2)
                        #print("\n")
                        current_x = float(room_lookup[split_text[1]][0])
                        current_y = float(room_lookup[split_text[1]][1])
                        current_z = float(room_lookup[split_text[1]][0])
                        print("--------- INITIAL LOCATION ----------")
                        print("ACTUAL LOC: %f, %f, %f\n" % (current_x, current_y, current_z))

                        broadcast_data(self.s_sock, text2)
                        get_rss_flag = 1

                        #op_started = 1

            else:
                #print("Connected: %d" % connected)
                if cycle_on == 0 and connected == 1:
                    cycle_on = 1

                    print("\t\t\t\tSTATUS: Getting battery level...")
                    text = "get_batt"
                    #time.sleep(0.1)
                    broadcast_data(self.s_sock, text)
                    get_batt_flag = 1
                    while get_batt_flag == 1:
                        #print("Getting battery level")
                        if self.running:
                            pass
                        else:
                            break
                    #print("Battery level obtained")
                    #print(batt)

                    command = path_planning()

                    print ("\t\t\t\tSTATUS: Executing command %d..." % int(command))
                    #print ("\t\t\t\tSTATUS: Sending command %d..." % int(command))
                    text = "command " + str(command)
                    #time.sleep(0.1)
                    broadcast_data(self.s_sock, text)
                    while command_done == 0:
                        #pass
                        if self.running:
                            pass
                        else:
                            break

                    if self.running == 0:
                        break

                    #if command == 11:
                    #    # INSERT CODE FOR CONNECT TO STATION HERE AFTER HANDOFF
                    #    connected = 0
                    #    print("\t\t\t\tSTATUS: Starting handoff")
                    #    #temporarily, connect to state 1
                    #    text = "connect 1"
                    #    broadcast_data(self.s_sock, text)
                        #connecting_flag = 1
                        #while connecting_flag == 1:
                    #    while connected == 0:
                    #        if self.running:
                    #            pass
                    #        else:
                    #            break
                    #    print("\t\t\t\tSTATUS: Handoff done")

                    #print("hey " + str(command_done) + " " + str(get_rss_flag))
                    command_done = 0
                    #time.sleep(0.2)
                    print ("\t\t\t\tSTATUS: Getting RSSI...")
                    text = "get_rssi"
                    #time.sleep(0.1)
                    broadcast_data(self.s_sock, text)
                    get_rss_flag = 1
                    while get_rss_flag == 1:
                        #pass
                        if self.running:
                            pass
                        else:
                            break

                    if self.running == 0:
                        break

                    print ("\t\t\t\tSTATUS: Getting DR location...")
                    text = "get_dr_loc"
                    #time.sleep(0.1)
                    broadcast_data(self.s_sock, text)
                    get_dr_flag = 1
                    while get_dr_flag == 1:
                        #pass
                        if self.running:
                            pass
                        else:
                            break

                    if self.running == 0:
                        break

                    #print(cycle_on)
                    print ("\t\t\t\tSTATUS: Computing actual location...")
                    compute_actual_loc()
                    print ("ACTUAL LOC: %0.3f %0.3f %0.3f" % (current_x, current_y, current_z))
                    print ("\t\t\t\tSTATUS: Done computing actual location...")

                    ##### INSERT IR CODE HERE

            #print("Op started: %d" % op_started)
            time.sleep(0.2)

        print("Thread exited while loop")
        sys.exit()
    def kill(self):
        self.running = 0
        print(self.running)
        print("killed")


#import fingerprint database
def import_db(station_count):
    global csv_data
    global fp_db

    #db = open("rss_db_427.csv", "r")
    #db = open("dummy_db1.csv", "r")
    db = open("rss_db_514.csv", "r")
    db_content = db.read()
    db.close()

    csv_data = db_content.split('\n')

    fp_db = {}
    fp_db['X'] = []
    fp_db['Y'] = []
    fp_db['Z'] = []

    for i in range (1, station_count + 1):
        key = "station" + str(i)
        fp_db[key] = []

    for i in range(0, len(csv_data) - 1):
        split_data = csv_data[i].split(',')

        fp_db['X'].append(split_data[0])
        fp_db['Y'].append(split_data[1])
        fp_db['Z'].append(split_data[2])

        for j in range(1, station_count + 1):
            key = "station" + str(j)
            fp_db[key].append(split_data[j+2])


# Location computation from fingerprinting
# KWNN with Dynamic Subarea Method
def compute_loc(station_count, measured_rss):

    global radius
    K = 2

    #print("1")
    index_knn = []

    D = []
    weight = []
    radius = 3 #radius of dynamic subarea

    #print("2")
    #computing euclidean distances and storing them to list D
    for i in range(0, len(csv_data) - 1):
        num = 0
        for j in range(0, STATION_COUNT):
            key = "station" + str(j+1)
            num = num + pow((int(fp_db[key][i]) - int(measured_rss[j])), 2)

        D.append(math.sqrt(num))

    #print("3")

    #print(D)

    #checking if there is a point wherein the
    #euclidean distance is 0
    for i in range(0, len(csv_data) - 1):
        if D[i] == 0:
            loc = [float(fp_db['X'][i]), float(fp_db['Y'][i]), float(fp_db['Z'][i])]
            return loc
    #print("4")

    #computing weights from euclidean distances
    #print(range(0,len(csv_data)-1))
    for i in range(0, len(csv_data) - 1):
        num = 1 / D[i]
        weight.append(num)
    #print("5")
    #print(weight)

    #storing index of K nearest neighbors to list index_knn
    #for i in range(0, K):
    #    min_D = min(D)
    #    index = D.index(min_D)

    #    D[index] = 1000000
    #    index_knn.append(index)

    for i in range (0, len(data) - 1):
        if D[i] < radius:
            index_knn.append(i)

    #print("6")

    #checks if able to get certain neighbors using the set radius
    if len(index_knn) > 0 and len(index_knn) < K:
        K = len(index_knn)
    else:
        #storing index of K nearest neighbors to list index_knn
        index_knn.clear()
        for i in range(0, K):
            min_D = min(D)
            index = D.index(min_D)

            D[index] = 1000000
            index_knn.append(index)

    #print(K)
    #print(index_knn)
    #print("K: %d" % K)
    #print("7")
    #print("lol3")

    #print('\n')
    #print(index_knn)

    #getting the location by using the formula for KWNN
    # K nearest neighbors

    denominator = 0
    for i in range (0, K):
        denominator = denominator + (weight[index_knn[i]])

    #print ("K: %d" % K)
    #print ("denominator: %0.5f" % denominator)
    #print("8")
    #print("lol4")

    x = 0
    for i in range(0, K):
        x = x + (float(fp_db['X'][index_knn[i]]) * weight[index_knn[i]])
    #print("9")
    x = x / denominator
    #print("10")
    #print("lol5")

    y = 0
    for i in range(0, K):
        y = y + (float(fp_db['Y'][index_knn[i]]) * weight[index_knn[i]])
    #print("11")
    y = y / denominator
    #print("9")
    #print("lol6")

    z = 0
    for i in range(0, K):
        z = z + (float(fp_db['Z'][index_knn[i]]) * weight[index_knn[i]])
    #print("13")
    z = z / denominator
    #print("14")
    #print("lol7")

    #print('\n')
    #print(weight)


    #print('\n')
    #loc = ["{0:.2f}".format(x), "{0:.2f}".format(y), "{0:.2f}".format(z)]
    loc = [x, y, z]
    #print("15")
    #print (loc)
    #print("%.2f, %.2f, %.2f" % (x, y, z))
    #loc = [0, 0, 0,]
    #print (loc)
    return loc

# Actual location computation
def compute_actual_loc():

    global radius

    global current_x
    global current_y
    global current_z

    global cycle_on

    global dr_loc
    global fp_loc
    global old_fp_loc

    #print(fp_loc)
    #print(dr_loc)

    ###### INSERT CODE FOR ACTUAL LOCATION COMPUTATION - FINGERPRINT + DEAD RECKONING
    delta_x = fp_loc[0] - current_x
    delta_y = fp_loc[1] - current_y
    delta_z = fp_loc[2] - current_z
    d_fp = math.sqrt(pow(delta_x, 2) + pow(delta_y, 2) + pow(delta_z, 2))

    delta_x = dr_loc[0] - current_x
    delta_y = dr_loc[1] - current_y
    delta_z = dr_loc[2] - current_z
    d_dr = math.sqrt(pow(delta_x, 2) + pow(delta_y, 2) + pow(delta_z, 2))

    if d_fp == 0:
        r = radius
    elif d_dr == 0:
        r = 0
    else:
        r = (1 / d_fp) / ((1 / d_fp) + (1 / d_dr))

    if (old_fp_loc[0] == fp_loc[0] and old_fp_loc[1] == fp_loc[1] and old_fp_loc[2] == fp_loc[2]):
        current_x = dr_loc[0]
        current_y = dr_loc[1]
        current_z = dr_loc[2]

    else:
        current_x = ((1 - r) * dr_loc[0]) + (r * fp_loc[0])
        current_y = ((1 - r) * dr_loc[1]) + (r * fp_loc[1])
        current_z = ((1 - r) * dr_loc[2]) + (r * fp_loc[2])

    #current_x = dr_loc[0]
    #current_y = dr_loc[1]
    #current_z = dr_loc[2]
    old_fp_loc[0] = fp_loc[0]
    old_fp_loc[1] = fp_loc[1]
    old_fp_loc[2] = fp_loc[2]

    # Clear cycle flag
    cycle_on = 0

def path_planning():

    global current_x
    global current_y
    global current_z

    global orientation

    global command

    global batt

    ##### INSERT JED'S CODE HERE
    global messageOut
    global messageIn

    #posX = 0        # The drone's current y-coordinate position
    #posY = 0        # The drone's current y-coordinate position
    #currRot = 1     # The drone's current orientation
    #flag = 0
    #print("Initialized!")
    #while flag == 0:
    # Use a flag wherein code executes only on flag == 0
    messageOut = str(current_x) + "," + str(current_y) + "," + str(orientation) + "," + str(batt)
    #print("messageOut = " + messageOut)
    sendSocket.send_string(messageOut)
    messageIn = sendSocket.recv()
    #print(messageIn)
    #print("messageIn = " + messageIn.decode("utf-8"))
    messageInString = messageIn.decode("utf-8")
    print("UNITY COMMAND: %s - %s" % (messageInString, commandLookup[int(messageInString)]))
    #print(messageInString)

    time.sleep(0.2)       # For delay purposes

    # temporary command - always forward
    #command = 1
    command = int(messageInString)


    return command



if __name__ == "__main__":

    # List to keep track of socket descriptors
    CONNECTION_LIST = []
    USERS = []
    NUMBER = []
    IP = []
    n = 0
    index = 0
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    STATION_COUNT = 3

    global RSS_data
    global csv_data
    global fp_db

    global get_rss_flag
    global op_started
    global cycle_on
    global command_done
    global get_dr_flag
    global connected
    global get_batt_flag

    global current_x
    global current_y
    global current_z

    global orientation

    global dr_loc
    global fp_loc
    global old_fp_loc

    global batt

    #global connecting_flag

    dr_loc = [0, 0, 0]
    fp_loc = [0, 0, 0]
    old_fp_loc = [0, 0, 0]

    import_db(STATION_COUNT)

    #print (csv_data)
    #print(len(csv_data))
    #print (fp_db)

    rss_data = {}
    rss_count = 0

    # FLAGS
    get_rss_flag = 0
    op_started = 0
    cycle_on = 0
    command_done = 0
    get_dr_flag = 0
    connected = 0
    get_batt_flag = 0


    # +x = 0, +y = 1, -x = 2, -y = 3
    # initial orientation is always +y
    orientation = 1

    #stopper = threading.Event()

    #PORT = int (input('Enter port number: '))
    PORT = 50191

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', PORT))
    server_socket.listen(1)

    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)
    print ("Chat server started on port " + str(PORT))

    sendContext = zmq.Context()
    sendSocket = sendContext.socket(zmq.REQ)
    sendSocket.connect("tcp://localhost:12345")
    print("Initialized!")
    #handler = SignalHandler(stopper)
    #signal.signal(signal.SIGINT, handler)


    thread_start = 0

    server_input = commanding_thread(server_socket)
    #server_input.start()


    try:
        while 1:
            # Get the list sockets which are ready to be read through select
            #print("While 1")
            read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[],0)
            #print("while in main")
            for sock in read_sockets:
                #New connection
                if sock == server_socket:
                    # Handle the case in which there is a new connection recieved through server_socket
                    sockfd, addr = server_socket.accept()
                    CONNECTION_LIST.append(sockfd)
                    print ("Client (%s, %s) connected" % addr)
                    USERS.append(addr[0])
                    IP.append(addr[0])
                    NUMBER.append(addr[1])
                    n = n + 1
                    broadcast_data(sockfd, "[%s:%s] entered room" % addr)

                    if len(CONNECTION_LIST) == (STATION_COUNT + 1) and thread_start == 0:
                        #server_input = commanding_thread(server_socket)
                        server_input.start()
                        thread_start = 1
                        #print ("hey")


                #Some incoming message from a client
                else:
                    addr1 = sock.getpeername()
                    index = NUMBER.index(addr1[1])

                    # Data recieved from client, process it
                    try:

                        #In Windows, sometimes when a TCP program closes abruptly,
                        # a "Connection reset by peer" exception will be thrown
                        rcv_data = sock.recv(RECV_BUFFER)
                        data = rcv_data.decode('ascii')

                        if data :
                            username = USERS[index]
                            #out = username + ": " + data
                            #print (data)

                            ####  HERE

                            if get_rss_flag == 1:
                                #print ("hi")
                                if rss_count < STATION_COUNT:


                                    if " " in data:
                                        #print("DATA: " + data)
                                        split_data = data.split(" ")

                                        if split_data[0] == "rss":
                                            rss_data[split_data[1]] = split_data[2]

                                            rss_count += 1
                                            #print ("rss count: %d" % rss_count)
                                            print("S%d RSSI: %d" % (int(split_data[1]), int(split_data[2])))


                                            if rss_count == STATION_COUNT:

                                                #print (rss_data)
                                                #to_db = str(x) + "," + str(y) + "," + str(z) + ","
                                                measured_rss = []

                                                for i in range (1, STATION_COUNT + 1):

                                                    #measured_rss = measured_rss + rss_data[str(i)]
                                                    measured_rss.append(int(rss_data[str(i)]))

                                                if op_started == 0:
                                                    op_started = 1
                                                    print ("\t\t\t\tSTATUS: Finding a station...")
                                                    minimum = min(measured_rss)
                                                    #print(measured_rss)
                                                    print(minimum)
                                                    station = measured_rss.index(minimum) + 1
                                                    print("\t\t\t\tSTATUS: Connecting to Station %d..." % station)
                                                    text = "connect " + str(station)
                                                    #text = "connect 2"
                                                    #print("Text")
                                                    broadcast_data(server_socket, text)
                                                    #print("Text broadcasted")

                                                else:
                                                    print ("\t\t\t\tSTATUS: Done getting RSSI...")

                                                    print ("\t\t\t\tSTATUS: Computing fingerprint location...")
                                                    #print(measured_rss)
                                                    fp_loc = compute_loc(STATION_COUNT, measured_rss)
                                                    #print(fp_loc)
                                                    #print("heyyyyy")
                                                    #print ("FP LOC: " + str(fp_loc[0]) + " " + str(fp_loc[1]) + " " + str(fp_loc[2]))
                                                    print ("FP LOC: %0.3f %0.3f %0.3f" % (float(fp_loc[0]), float(fp_loc[1]), float(fp_loc[2])))
                                                    #compute_loc1(STATION_COUNT, measured_rss)
                                                    print ("\t\t\t\tSTATUS: Done fingerprint computing location...")

                                                rss_data.clear()
                                                rss_count = 0
                                                get_rss_flag = 0

                            if " " in data:
                                split_data = data.split(" ")

                                if split_data[0] == "Connected":
                                    #print("llalalalalala")
                                    print("\t\t\t\tSTATUS: " + data)
                                    connected = 1
                                    #connecting_flag = 0

                                elif data == "Command done":
                                    #print(get_rss_flag)
                                    print("\t\t\t\tSTATUS: " + data)
                                    command_done = 1

                                elif split_data[0] == "dr_loc":
                                    dr_loc = [float(split_data[1]), float(split_data[2]), float(split_data[3])]
                                    orientation = int(split_data[4])
                                    print ("DR LOC: " + str(dr_loc[0]) + " " + str(dr_loc[1]) + " " + str(dr_loc[2]))
                                    print ("\t\t\t\tSTATUS: Done getting dead reckoning location...")
                                    get_dr_flag = 0

                                elif split_data[0] == "batt":
                                    #print(data)
                                    batt = int(split_data[1])
                                    print ("BATTERY: %d" % batt)
                                    print ("\t\t\t\tSTATUS: Done getting battery level...")
                                    get_batt_flag = 0


                        else :
                            username = USERS[index]
                            broadcast_data(sock, "\r%s is offline\n" % username)
                            print ("%s is offline 1" % username)
                            del NUMBER[index]
                            del USERS[index]
                            del IP[index]
                            #print NUMBER
                            n = n - 1
                            sock.close()
                            CONNECTION_LIST.remove(sock)
                            server_input.kill()
                            server_input.join()
                            continue

                    except:
                        username = USERS[index]
                        broadcast_data(sock, "%s is offline" % username)
                        print ("%s is offline 2" % username)
                        del NUMBER[index]
                        del USERS[index]
                        del IP[index]
                        n = n - 1
                        sock.close()
                        CONNECTION_LIST.remove(sock)
                        server_input.kill()
                        server_input.join()
                        #print("Killed")
                        continue

    except KeyboardInterrupt:
        #server_input._stop()

        server_input.kill()
        server_input.join()
        server_socket.close()

    #server_socket.close()
