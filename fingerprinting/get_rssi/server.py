import socket, select, time, sys, threading, signal
 
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

#class SignalHandler:
#    stopper = None
#    
#    def __init__(self, stopper):
#        self.stopper = stopper
#
#    def __call__(self, signum, frame):
#        self.stopper.set()
#
#        sys.exit(0)

class Text_Input(threading.Thread):

    #stopper = None

    def __init__(self, s_sock):
        threading.Thread.__init__(self)
        self.s_sock = s_sock
#        self.stopper = stopper
        self.running = 1
    def run(self):
        global get_rss_flag
        global x
        global y
        global z

        while self.running == True:
        #while not self.stopper.is_set():
            text = input('')
            broadcast_data(self.s_sock, text)
            #print (get_rss_flag)
            if " " in text:
                split_text = text.split(" ")

                if split_text[0] == "get_rssi":
                    get_rss_flag = 1
                    x = split_text[1]
                    y = split_text[2]
                    z = split_text[3]
                    print ("Getting RSSI...")
                    while get_rss_flag:
                        pass

            else:

                if text == "get_rssi":
                    get_rss_flag = 1
                    x = 0
                    y = 0
                    z = 0
                    print ("Getting RSSI...")
                    while get_rss_flag:
                        pass

            time.sleep(0)
    def kill(self):
        self.running = 0
    
    #def stop(self):

if __name__ == "__main__":
     
    # List to keep track of socket descriptors
    CONNECTION_LIST = []
    USERS = []
    NUMBER = []
    IP = []
    n = 0
    index = 0
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    STATION_COUNT = 2

    global RSS_data
    global get_rss_flag
    global x
    global y
    global z
    

    rss_data = {}
    get_rss_flag = 0
    rss_count = 0

    #stopper = threading.Event()
        
    PORT = int (input('Enter port number: '))

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', PORT))
    server_socket.listen(1)
 
    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)
    print ("Chat server started on port " + str(PORT))  

    #handler = SignalHandler(stopper)
    #signal.signal(signal.SIGINT, handler)

    server_input = Text_Input(server_socket)
    server_input.start()

    
    try:
        while 1:
            # Get the list sockets which are ready to be read through select
            read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])

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
                            out = username + ": " + data
                            print (out)

                            ####  HERE
                            
                            if get_rss_flag == 1:
                                #print ("hi")
                                if rss_count < STATION_COUNT:
                                    if " " in data:
                                        split_data = data.split(" ")

                                        if split_data[0] == "rss":
                                            rss_data[split_data[1]] = split_data[2]
                                            
                                            rss_count += 1
                                            #print ("rss count: %d" % rss_count)

                                            if rss_count == STATION_COUNT:

                                                #print (rss_data)
                                                to_db = str(x) + "," + str(y) + "," + str(z) + ","
                                                #print ("leaaaaaaa")
                                                #print (to_db)

                                                for i in range (1, STATION_COUNT + 1):

                                                    to_db = to_db + rss_data[str(i)]

                                                    if i != STATION_COUNT:
                                                        to_db = to_db + ","

                                                print (to_db)
                                                to_db = to_db + "\n"
                                                
                                                #print ("Done")
                                                #print (x)
                                                #print (y)
                                                #print (z)
                                                print ("Done getting RSSI...")
                                                
                                                db = open("rss_db.csv", "a")
                                                db.write(to_db)
                                                db.close()

                                                rss_data.clear()
                                                rss_count = 0
                                                get_rss_flag = 0

                                    
                        else :
                            username = USERS[index]
                            broadcast_data(sock, "\r%s is offline\n" % username)
                            print ("%s is offline" % username)
                            del NUMBER[index]
                            del USERS[index]
                            del IP[index]
                            #print NUMBER
                            n = n - 1
                            sock.close()
                            CONNECTION_LIST.remove(sock)
                            continue
                                             
                    except:
                        username = USERS[index]
                        broadcast_data(sock, "%s is offline" % username)
                        print ("%s is offline" % username)
                        del NUMBER[index]
                        del USERS[index]
                        del IP[index]
                        n = n - 1
                        sock.close()
                        CONNECTION_LIST.remove(sock)
                        continue
 
    except KeyboardInterrupt:
        server_input.kill()
        #server_input.join()
        server_socket.close()

    #server_socket.close()
