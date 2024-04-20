import serial_comm as sc

import inverse_kinematics




if __name__ == '__main__':

    manip = sc.Controller()

    try:
            manip.connect()

            x, y, z, M = [float(item) for item in  input("Insert coords and mag as:  x y z M").split() ]

            dh1, dh2, dh3 = inverse_kinematics.get_dh_angles_for_coord(x,y,z)




            

    finally:
        manip.close_connection()
