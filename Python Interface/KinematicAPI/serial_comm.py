import serial
import time
import os

class Controller:
    def __init__(self):
        self.ser = None
        self.default_position = [0,0,0]
        self.cur = None
        self.magnet = False

        self.buadrate = 115200
        self.connect()

    def array_to_string(self, arr):

        # string must look like  "iii iii iii i". it must be 13 characters long, all angles will be 1-3 digits, so we need to pad with zeros

        # one liner
        return " ".join([str(i).zfill(3) for i in arr])

        
    def connect(self):
        options = os.listdir("/dev")
        options = [i for i in options if "cu.usbmodem" in i]

        if len(options) == 0:
            print("No serial options found")
            return
        if len(options) > 1:
            print("Choose a serial option:")
            for i in range(len(options)):
                print(f"{i}: {options[i]}")
            choice = int(input())

            # #  choose the one with a 3 in it
            # choice = 0
            # for i in range(len(options)):
            #     if "3" in options[i]:
            #         choice = i
            #         break

        else:
            choice = 0

        self.ser = serial.Serial(f"/dev/{options[choice]}", self.buadrate)
        time.sleep(2)
        print("Connected to serial")

    def send_signal(self, angles):
        s = self.array_to_string(angles)
        self.ser.write(s.encode())
        


        

    def close_connection(self):
        self.ser.close()
        print("Connection closed")
        time.sleep(0.1)



        
if __name__ == "__main__":
    c = Controller()
    print(c.array_to_string([1,2,3]))
    