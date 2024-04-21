import numpy as np


#LINK LENGTHS in CM
A1 = 9.2  # Base to the shoulder pin
A2 = 13.5 # Bicep
A3 = 14.7 # Elbow_Joint to End_Effector

#DEG



def deg_to_rad(deg):
    return (deg/180.0) * np.pi


def make_htm(theta0, theta1, theta2):
# HOMOGENIZE MATRICIES

    #ROTO MATRS
    R0_1 = np.matrix( 
        [
        [np.cos(theta0), 0, np.sin(theta0)],
        [np.sin(theta0), 0, -np.cos(theta0)],
        [0, 1, 0]
        ] )

    R1_2 = np.matrix( 
        [
        [np.cos(theta1), -np.sin(theta1), 0],
        [np.sin(theta1), np.cos(theta1), 0],
        [0, 0, 1]
        ] )

    R2_3 = np.matrix( 
        [
        [np.cos(theta0), -np.sin(theta0), 0],
        [np.sin(theta0), np.cos(theta0), 0],
        [0, 0, 1]
        ] )
    
    #DISPO MATRS
    D0_1 = np.matrix([[0], 
                    [0], 
                    [A1] ])

    D1_2 = np.matrix([ 
                    [A2 * np.cos(theta1)],
                    [A2 * np.sin(theta1)], 
                    [0] 
                    ])

    D2_3 = np.matrix([ 
                    [A3 * np.cos(theta2)],
                    [A2 * np.sin(theta2)],
                    [0] 
                    ])



    H0_1 = np.concatenate((R0_1, D0_1), 1)
    H0_1 = np.concatenate( (  H0_1, [[0,0,0,1]]  ), 0)

    H1_2 = np.concatenate((R1_2, D1_2), 1)
    H1_2 = np.concatenate( (  H1_2, [[0,0,0,1]]  ), 0)

    H2_3 = np.concatenate((R2_3, D2_3), 1)
    H2_3 = np.concatenate( (  H2_3, [[0,0,0,1]]  ), 0)


    H0_3 = (H0_1 @ H1_2) @ H2_3

    #print(H0_3)

    # with built in x <--> y transformation swap
    return {'x':-H0_3[1,3], 'y': H0_3[0,3], 'z': H0_3[2,3]}

def get_xyz(t1d, t2d, t3d):
    t1r, t2r, t3r = [deg_to_rad(t) for t in [t1d, t2d, t3d]]



    xyz_dict = make_htm(t1r, t2r, t3r)

    return xyz_dict


if __name__ == "__main__":
    d = get_xyz(45, 45, -45)
    print(d)