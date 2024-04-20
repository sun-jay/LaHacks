import json_interface
from scipy.spatial import KDTree


print("parsing")
angles_to_coords = json_interface.read_json_to_dict()


coord_to_angles = { (coords_dict["x"], coords_dict["y"], coords_dict["z"]) : ang_str \
                   for ang_str,coords_dict in angles_to_coords.items()}


print("done")





def get_dh_angles_for_coord(x,y,z):
    """
     coordinates in CM, angles given in DH degrees.
    """
    # Suppose your 4 million tuples are in a list called points
    points = list(coord_to_angles.keys())

    tree = KDTree(points)
    print("making tree")

    # To find the closest point to a new tuple (x, y, z)
    closest_distance, closest_index = tree.query((x, y, z))
    print("queried tree")

    closest_angles_str = coord_to_angles[points[closest_index]]

    a1, a2, a3 = [ int(ang) for ang in closest_angles_str.split()]
    a1 /= 2
    a1 = int(a1)

    return a1, a2, a3



if __name__ == "__main__":

    angles= get_dh_angles_for_coord(7, 15, 0)
    a1, a2, a3 = angles

    print(a1,a2,a3)