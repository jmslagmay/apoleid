while self.running == True:
            
        #while not self.stopper.is_set():
            text = input('')
#            if (get_rss_flag == 0):
            #text = "get_rssi"
            

            broadcast_data(self.s_sock, text)
            #print("hey")
            #print (get_rss_flag)
            if " " in text:
                split_text = text.split(" ")

                if split_text[0] == "get_rssi":
                    get_rss_flag = 1
                    if op_started == 1:
                        print ("Getting RSSI...")
                    
                    #x = split_text[1]
                    #y = split_text[2]
                    #z = split_text[3]
                    #print ("Getting RSSI...")
                    while get_rss_flag:
                        pass

                elif split_text[0] == "start":
                    print ("Starting drone operation...")
                    text2 = "get_rssi " + str(room_lookup[split_text[1]][0]) + " " + str(room_lookup[split_text[1]][1]) + " " + str(room_lookup[split_text[1]][2])
                    get_rss_flag = 1
                    #print(text2)
                    time.sleep(0.1)
                    broadcast_data(self.s_sock, text2)

                #elif split_text[0] == "hey":
                #    text2 = "get_rssi " + str(room_lookup[split_text[1]][0]) + " " + str(room_lookup[split_text[1]][1]) + " " + str(room_lookup[split_text[1]][2])
                #    print(text2)
   
            else:

                if text == "get_rssi":
                    get_rss_flag = 1
                    if op_started == 1:
                        print ("Getting RSSI...")
                    
                    #x = 0
                    #y = 0
                    #z = 0
                    #print ("Getting RSSI...")
                    while get_rss_flag:
                        pass

                #elif text == "start":
                #    print ("Starting drone operation...")
                #    text2 = "get_rssi"
                #    get_rss_flag = 1
                    #print(text2)
                #    time.sleep(0.1)
                #    broadcast_data(self.s_sock, text2)
