import zmq
import time

if __name__ == '__main__':
    global messageOut
    global messageIn
    sendContext = zmq.Context()
    sendSocket = sendContext.socket(zmq.REQ)
    sendSocket.connect("tcp://localhost:12345")
    posX = 0        # The drone's current y-coordinate position
    posY = 0        # The drone's current y-coordinate position
    currRot = 1     # The drone's current orientation
    flag = 0
    print("Initialized!")
    while flag == 0:
        # Use a flag wherein code executes only on flag == 0
        messageOut = str(posX) + "," + str(posY) + "," +str(currRot)
        print("messageOut = " + messageOut)
        sendSocket.send_string(messageOut)
        messageIn = sendSocket.recv()
        #print("messageIn = " + messageIn.decode("utf-8"))
        messageInString = messageIn.decode("utf-8")
        #print(messageInString)
        if messageInString == "1":
            """print("currRot = " + str(currRot))
            if currRot == 0:
                posX += 1
            elif currRot == 1:
                posY += 1
            elif currRot == 2:
                posX -= 1
            elif currRot == 3:
                posY -= 1"""
            # Send "forward" command
        elif messageInString == "5":
            """currRot += 1
            if currRot == 4:
                currRot = 0"""
            # Send "yaw left" command
        elif messageInString == "6":
            """currRot -= 1
            if currRot == -1:
                currRot = 3"""
            # Send "yaw right" command
        else:
            # Stall
            pass
        time.sleep(2)       # For delay purposes