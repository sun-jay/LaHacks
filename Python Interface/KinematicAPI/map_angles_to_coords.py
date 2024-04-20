import serial_comm
import HTM



def make_map(manip):

    map_dict = dict()
    for servo_a1 in range(0,181):
        for servo_a2 in range(0,181):
            for servo_a3 in range(0,181):
                try:
                    manip.check_angles(servo_a1, servo_a2, servo_a3)
                    #if the servo angles are valid, continue

                    


                    map_dict[f'{a1} {a2} {a3}'] = HTM.get_xyz(a1, a2, a3) #angles in degreez



                except AssertionError as e:
                    print(e)
                    continue


    return 
if __name__ == "__main__":
    manip = serial_comm.Controller()
    make_map(manip)