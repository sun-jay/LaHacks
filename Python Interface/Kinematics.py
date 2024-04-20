# open source library from https://github.com/contagon/eezy_arm_ros


import numpy as np
from scipy.spatial.transform import Rotation as scipy_R

NUM_JOINTS = 3


def deg2rad(deg : float) -> float:
    """Helper function converts degrees to radians

    Args:
        deg (float): Angle in degrees

    Returns:
        float: Angle in radians
    """
    return deg * np.pi / 180.


def rotate_x_se3(theta : float, radians=False) -> np.array:
    """Computes a transformation matrix of a rotation of theta about the x axis

    Args:
        theta (float): Angle, in degrees or radians
        radians (bool, optional): Determines if angle is in degrees or radians. Defaults to False (degrees).
    
    Returns:
        np.array: 4x4 transformation matrix (rotation only)
    """
    if not radians:
        theta = deg2rad(theta)

    return np.array([[1, 0,              0,             0],
                     [0, np.cos(theta), -np.sin(theta), 0],
                     [0, np.sin(theta),  np.cos(theta), 0],
                     [0, 0,              0,             1]])


def rotate_y_se3(theta : float, radians=False) -> np.array:
    """Computes a transformation matrix of a rotation of theta about the y axis

    Args:
        theta (float): Angle, in degrees or radians
        radians (bool, optional): Determines if angle is in degrees or radians. Defaults to False (degrees).
    
    Returns:
        np.array: 4x4 transformation matrix (rotation only)
    """
    if not radians:
        theta = deg2rad(theta)

    return np.array([[ np.cos(theta), 0, np.sin(theta), 0],
                     [ 0,             1, 0,             0],
                     [-np.sin(theta), 0, np.cos(theta), 0],
                     [0,              0, 0,             1]])


def rotate_z_se3(theta : float, radians=False) -> np.array:
    """Computes a transformation matrix of a rotation of theta about the z axis

    Args:
        theta (float): Angle, in degrees or radians
        radians (bool, optional): Determines if angle is in degrees or radians. Defaults to False (degrees).
    
    Returns:
        np.array: 4x4 transformation matrix (rotation only)
    """
    if not radians:
        theta = deg2rad(theta)

    return np.array([[np.cos(theta), -np.sin(theta), 0, 0],
                     [np.sin(theta),  np.cos(theta), 0, 0],
                     [0,              0,             1, 0],
                     [0,              0,             0, 1]])


def translate_se3(t_row_vector : np.array) -> np.array:
    """Creates a transformation matrix that is strictly a translation. np.concatenate raises an error 
    if t_row_vector is not the correct dimension.

    Args:
        t_row_vector (np.array): Translation vector (1x3 row vector)

    Returns:
        np.array: 4x4 transformation matrix (translation only)
    """   
    T = np.eye(4)
    T[:3,3] = t_row_vector
    return T


class EezyBotArm:
    def __init__(self) -> None:
        # Number of joints (base, vertical arm, horizontal arm)
        self.n = NUM_JOINTS
        # Keep track of the end effector status (open/closed)
        self.ee_closed = True

        # Robot physical parameters
        self._l1 = 92  # mm
        self._l2 = 135  # mm
        self._l3 = 147  # mm
        self._l4 = 87  # mm

        self.curr_q = np.zeros(3)


    def compute_A_matrix(self, q : list, joint_idx : int) -> np.array:
        """Computes the transformation matrix from the given joint to the end of the link. With the 
        EEZYbotARM MK2 it does not necessarily follow DH convention. The horizontal link and the end effector 
        are at a fixed orientation (level to the ground) so we have to negate the rotation angle of joint for 
        joints 1 and 2

        Args:
            q (list): Joint angles in degrees
            joint_idx (int): Joint index of the robot

        Returns:
            np.array: 4x4 transformation matrix
        """
        if joint_idx == 0:
            A = rotate_z_se3(q[0]) @ translate_se3(np.array([0, 0, self._l1])) @ rotate_x_se3(-np.pi/2, radians=True)
        elif joint_idx == 1:
            A = rotate_z_se3(q[1]) @ rotate_z_se3(-np.pi/2, radians=True) @ translate_se3(np.array([self._l2, 0, 0])) @ rotate_z_se3(np.pi/2, radians=True) @ rotate_z_se3(-q[1])
        elif joint_idx == 2:
            A = rotate_z_se3(q[2]) @ translate_se3(np.array([self._l3, 0, 0])) @ rotate_z_se3(-q[2])
        elif joint_idx == 3:
            A = translate_se3(np.array([self._l4, 0, 0])) @ rotate_x_se3(np.pi/2, radians=True)
        else:
            raise ValueError('Invalid joint! Expects 0 - 3')

        return A

    def forward_kinematics(self, q : list, starting_link=0, ending_frame=NUM_JOINTS, base=True, ee=True) -> np.array:
        """Returns the transformation matrix from one link to another given a q.
           Defaults to calculating fk from the base to the end effector.

        Args:
            q (list): Joint angles in degrees.
            starting_link (int, optional): The link from which to calculate fk. Defaults to 0 (base frame).
            ending_frame (int, optional): The link to which we want fk calculated. Defaults to NUM_JOINTS (end effector frame).
            base (bool, optional): If true and starting index is 0, then base transform will be included. Defaults to True.
            ee (bool, optional): If true and index ends at nth frame, then end effector transforma will be included. Defaults to True.

        Returns:
            np.array: 4x4 transformation matrix from the 'starting_link' to the 'ending_frame'
        """
        T = np.eye(4) 

        for i in range(starting_link, ending_frame):
            T = T @ self.compute_A_matrix(q, i)

        if ee == True and ending_frame == NUM_JOINTS:
            T = T @ self.compute_A_matrix(q, 3)

        return T

    def jacob(self, q : list, idx=NUM_JOINTS, base=True, ee=True) -> np.array:
        """Returns the Jacobian of link at idx in the base frame at configuration q.

        Args:
            q (list) : Joint angles in degrees.
            idx (int, optional): The link to which we want the Jacobian. Defaults to NUM_JOINTS (ee frame).
            base (bool, optional): If true and starting index is 0, then base transform will be included. Defaults to True.
            ee (bool, optional): If true and index ends at nth frame, then end effector transforma will be included. Defaults to True.

        Returns:
            np.array: 6x3 Jacobian of idx in the base frame.
        """
        J = np.zeros((6,3))

        Pe = self.forward_kinematics(q, ending_frame=idx, base=base, ee=ee)[:3,3]

        for i in range(idx):
            f = self.forward_kinematics(q, ending_frame=i, base=base, ee=ee)
            zi = f[:3,2]

            J[0:3, i] = np.cross(zi, Pe-f[:3,3])
            J[3:6, i] = zi

        return J

    def ik(self, p_des : list, q0 : list, max_iter=1000, tol=1e-3, K=5, method="damped") -> np.array:
        """Returns the required configuration q to be at position q_des.

        Args:
            p_des (list) : Desired position (x,y,z) in mm.
            q0 (list) : Initial configuration starting estimate.
            max_iter (int, optional) : Maximum number of iterations to perform. Defaults to 1000.
            tol (float, optional) : Stopping criteria. Algorithm stops if |error|^2 < tol. Defaults to 1e-6.
            K (float, optional): Gains for algorithm. Defaults to 5.
            method (str, optional) : IK method to use, either "damped" or "transpose". Defaults to "damped".

        """
        # setup initial conditions
        p_des = np.array(p_des, dtype='float')
        q = np.array(q0, dtype='float').copy()
        kd2 = np.eye(3)*.001
        if isinstance(K, float) or isinstance(K, int):
            K = np.eye(3)*K

        e = p_des - self.forward_kinematics(q)[:3,3]

        for i in range(max_iter):
            J = self.jacob(q)[:3,:]

            if method == "damped":
                # qdot = J.T @ np.linalg.inv(J@J.T + kd2) @ K @ e
                # Since J is square for us, we can just invert:)
                qdot = np.linalg.inv(J + kd2) @ K @ e
            elif method == "transpose":
                qdot = J.T @ K @ e

            q += qdot

            e = p_des - self.forward_kinematics(q)[:3,3]
            if e@e < tol:
                return q		




if __name__ == "__main__":
    e = EezyBotArm()

    coords = e.forward_kinematics([0, 0, 0])
    # extract the position
    print(coords[:3,3])
    print(e.ik([90, 90, 90], [0, 0, 0]))

