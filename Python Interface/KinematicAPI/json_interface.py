import json

FILENAME = 'angle_to_coord_map.json'

def write_dict_to_json(data):
    """
    Writes a dictionary to a JSON file.

    Parameters:
    - data: Dictionary to be stored.
    - filename: Name of the JSON file.
    """
    with open(FILENAME, 'w') as json_file:
        json.dump(data, json_file)


def read_json_to_dict():
    """
    Reads a JSON file and returns its contents as a dictionary.

    Parameters:
    - filename: Name of the JSON file.

    Returns:
    - Dictionary containing the contents of the JSON file.
    """
    with open(FILENAME, 'r') as json_file:
        data = json.load(json_file)
    return data
