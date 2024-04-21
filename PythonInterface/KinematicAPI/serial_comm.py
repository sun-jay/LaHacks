import serial
import time
import os

class Controller:
    def __init__(self):
        self.ser = None
        self.magnet = 0
        self.current_position = [None, None, None]
        self.default_position = "000 000 000 0"


        self.buadrate = 115200


    def curr_pos_to_string(self):

        # string must look like  "iii iii iii i". it must be 13 characters long, all angles will be 1-3 digits, so we need to pad with zeros

        # one liner
        return " ".join(     [str(i).rjust(3, "0") for i in self.current_position] + [str(int(self.mag))]  )





    ############ PUBLIC DOMAIN BELOW  ################
        
    def connect(self):
        options = os.listdir("/dev")
        options = [i for i in options if "cu.usbmodem" in i]

        if len(options) == 0:
            print("No serial options found")
            return
        if len(options) > 1:
            
            print("Choose a serial option:")
            # for i in range(len(options)):
            #     print(f"{i}: {options[i]}")
            # choice = int(input())

            for i, option in enumerate(options):
                if "3" in option:
                    choice = i


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
        print("Connected to serial.")

    def check_angles(self, a1, a2, a3):
        '''
        Here we will write conditions to not break the bot
        '''
        assert ( a1 in range(0, 181)), f"a1 not in servo range [0,180]. actual: {a1}"
        assert ( a2 in range(0, 181)), f"a1 not in servo range [0,180]. actual: {a2}"
        assert ( a2 in range(0, 181)), f"a1 not in servo range [0,180]. actual: {a2}"

        #stretch and scissor conditions

        #stretch condition -- max angle bw a2 & a3
        assert  a2 + a3 < 320, f"Stretch Condition Violated: a2: {a2}, a3: {a3}."


        #scissor condition -- min angle bw a2 & a3
        normalized_a3 = (-a3 +180)
        assert (   abs(normalized_a3 - a2) >  40  ), f"Scissor Condition Violated: a2: {a2}, a3: {a3}."
        assert (  normalized_a3 < a2 ), f"Arm-Order Condition Violated: a2: {a2}, a3: {a3}."

    def send_signal(self, a1, a2, a3, mag):

        #check the angles
        try:

            self.check_angles(a1, a2, a3)
            #if this raises no issues, continue

            #set the curr_poss and mag status
            self.current_position = [a1, a2, a3]
            self.mag = mag

            #turn it into a string
            angle_str = self.curr_pos_to_string()
            
            #send said string
            print("SENDING THIS STRING: ", angle_str.encode())
            self.ser.write(angle_str.encode())

        except AssertionError as e:
            print("Sending Angles Failed")
            print(e)

    def close_connection(self):
        self.ser.close()
        print("Connection closed")
        time.sleep(0.1)


    def servo_angs_to_dh_angs(self, sa1, sa2, sa3):

        #map sa1 from [0, 180]  --->  [-90 90]
        dh1 = sa1 - 90

        #map sa2 from [0,180] ----> [180, 0]
        dh2 = 180 - sa2

        #map sa3 from [0,180] ----> [0, -180]
        dh3 = -dh2 + (sa3 - 180)

        return dh1, dh2, dh3

if __name__ == "__main__":
    try: 
        manip = Controller()
        manip.connect()

        while(True):
            a1,a2,a3,M = [int(i) for i in input("Enter 3 angles and mag: 'a1 a2 a3 M': ").strip().split()]
            
            d1,d2,d3 = manip.servo_angs_to_dh_angs(a1,a2,a3)
            print(d1,d2,d3)
            
            manip.send_signal(a1,a2,a3,M)
    except AssertionError as e:
        print(e)
    finally:
        manip.close_connection()
    