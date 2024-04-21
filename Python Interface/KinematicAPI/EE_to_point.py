import serial_comm as sc

import inverse_kinematics
import time

def stryfe_points():
     
    points_list = [(-7, 14, 5, 0),(-5, 23, 5, 0),(6, 21 , 5, 0), (9, 15, 5, 0)]
    while(True):
            for p in points_list:
                s1, s2, s3 = inverse_kinematics.get_srvo_angles_for_coord_linear(p[0],p[1],p[2])
                print("ANGS ARE: ", s1,s2,s3)
                time.sleep(1.8)
                manip.send_signal(s1,s2,s3,0)

if __name__ == '__main__':

    manip = sc.Controller()

    try:
            manip.connect()
            
            
            time.sleep(1)

            manip.send_signal(90,90,180,0)

            time.sleep(5)

            while(True):
                x, y, z, M = [float(item) for item in  input("Insert coords and mag as:  x y z M: ").split() ]

                print("getting angs")
                s1, s2, s3 = inverse_kinematics.get_srvo_angles_for_coord_linear(x,y,z)

                print("ANGS ARE: ", s1,s2,s3)
                time.sleep(2)
                manip.send_signal(s1,s2,s3,M)



    finally:
        manip.close_connection()
