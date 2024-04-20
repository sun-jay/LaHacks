import serial_comm
import HTM



def make_map(manip):

    map_dict = dict()
    for x in range(0,181):
        for y in range(0,181):
            for z in range(0,181):
                try:
                    manip.check_angles(x, y, z)
                    #if the angles are valid, continue


                except AssertionError as e:
                    print(e)
                    continue


    return 
if __name__ == "__main__":
    manip = serial_comm.Controller()
    make_map(manip)