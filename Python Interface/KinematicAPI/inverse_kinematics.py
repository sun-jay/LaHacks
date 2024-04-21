import json_interface
#from scipy.spatial import KDTree


print("parsing...")
angles_to_coords = json_interface.read_json_to_dict()
print("JSON LOADED.")

# coord_to_angles = { (coords_dict["x"], coords_dict["y"], coords_dict["z"]) : ang_str \
#                    for ang_str,coords_dict in angles_to_coords.items()}


print("done")


def flip_dict(angles_to_coords):

    return { (coords_dict["x"], coords_dict["y"], coords_dict["z"]) : ang_str \
                   for ang_str,coords_dict in angles_to_coords.items()}


# def get_dh_angles_for_coord_tree(x,y,z):
#     """
#      coordinates in CM, angles given in DH degrees.
#     """
#     # Suppose your 4 million tuples are in a list called points
#     points = list(coord_to_angles.keys())

#     tree = KDTree(points)
#     print("making tree")

#     # To find the closest point to a new tuple (x, y, z)
#     closest_distance, closest_index = tree.query((x, y, z))
#     print("queried tree")

#     closest_angles_str = coord_to_angles[points[closest_index]]

#     a1, a2, a3 = [ int(ang) for ang in closest_angles_str.split()]
#     a1 /= 2
#     a1 = int(a1)

#     return a1, a2, a3



def get_srvo_angles_for_coord_linear(x,y,z):
    """
     coordinates in CM, angles given in DH degrees.
    """

    coord_tup_to_angles_str = flip_dict(angles_to_coords)

    possible = []

    for coord_tup, angle_str in coord_tup_to_angles_str.items():
        flt_x = coord_tup[0]
        flt_y = coord_tup[1]
        flt_z = coord_tup[2]

        if (flt_x -0.2 < x < flt_x +0.2 ) \
            and (flt_y -0.2 < y < flt_y +0.2)\
            and (flt_z -0.2 < z < flt_z +0.2):


            possible.append( (coord_tup, angle_str)  )
    
    #print("POSS", possible)
    
    if len(possible) > 0 and possible[   int(len(possible)/2)   ]:
        ans = possible[   int(len(possible)/2)   ][1]
        a1, a2, a3 = [int(i) for i in ans.split()]
        #a1 =  ((a1 + 45)*2)
        
        a1 = (a1)
        print("A1 is:", a1)
        shift = abs(a1-90) * 2

        if a1<90:
            a1 = 90 - shift
            return 180-a1, a2, a3
        if a1>90:
            a1 = 90 + shift
            return 180-a1, a2, a3
        if a1 == 90:
            return 180-a1, a2, a3
    else:
        print("COORD NOT REACHABLE")
        # print("A1 IS: ", a1)
        # if a1 in range(0,91):
        #     a1 *=2
        # if a1 in range(91,181):
        #     a1 = 180 - a1 
        #     a1 = int(a1/2)
        



def get_closest_contender(possible, x, y, z):
    for coord_tup, ang_str in possible:
        pass


if __name__ == "__main__":

    a1, a2, a3 = get_srvo_angles_for_coord_linear(7, 20, 5)
    
    print(a1, a2 , a3)
    #a1, a2, a3 = angles

    #print(a1,a2,a3)