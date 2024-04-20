import serial_comm
import HTM

import json_interface

def make_map(manip):

    map_dict = dict()
    for servo_a1 in range(0,181):
        print(servo_a1)
        for servo_a2 in range(0,181):
            for servo_a3 in range(0,181):
                try:
                    manip.check_angles(servo_a1, servo_a2, servo_a3)
                    #if the servo angles are valid, continue

                    dh1, dh2, dh3 = manip.servo_angs_to_dh_angs(servo_a1, servo_a2, servo_a3)


                    map_dict[f'{servo_a1} {servo_a2} {servo_a3}'] = HTM.get_xyz(dh1, dh2, dh3) #angles in degreez



                except AssertionError as e:
                    #print(e)
                    continue

    json_interface.write_dict_to_json(map_dict)
    print(f"written to {json_interface.FILENAME}.")
    return 
if __name__ == "__main__":
    manip = serial_comm.Controller()
    make_map(manip)