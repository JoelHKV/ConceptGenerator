import json
import random
def return_sub_dict(whole_dict, filter_field_name, filter_value):
    #sub_dict = [value for value in whole_dict.values() if value[filter_field_name] == filter_value]
    sub_dict = {key: value for key, value in whole_dict.items() if value.get(filter_field_name) == filter_value}
    if not sub_dict:
        sub_dict = {}
    return sub_dict

def get_sample_underpresented(dimension_rating_data, dimension_name, dimension, sample_size):
    key_lengths = [(key, len(dimension_rating_data[key][dimension_name])) for key in dimension_rating_data]
    random.shuffle(key_lengths)
    key_lengths.sort(key=lambda x: x[1])
    smallest_length = key_lengths[0][1]
    print(smallest_length)
    random_sample = key_lengths[:sample_size]
    random.shuffle(random_sample)
    random_keys_list = [key for key, _ in random_sample]
    return random_keys_list, smallest_length 





def json_to_dict(file_path):
    try:
        with open(file_path, 'r') as file:
            this_dict = json.load(file)
            return this_dict
    except FileNotFoundError:
        print(f"Returning an empty dictionary.")
        return {}
        
def dict_to_json(file_path, data_dict):
    with open(file_path, 'w') as file:
        json.dump(data_dict, file)
        return

def dict_to_txt(file_path, data_dict):
    with open(file_path, "w") as file:
        for key, value in data_dict.items():
            line = f"{key}: {value}\n"
            file.write(line)
            
def txt_to_dict(file_path):
    data_dict = {}
    try:
        with open(file_path, "r") as file:
            for line in file:
                # Split each line by the ':' character to separate key and value
                key, value = line.strip().split(': ', 1)
                # Add the key-value pair to the dictionary
                data_dict[key] = value
    except FileNotFoundError:
        # Handle the case where the file is not found
        print(f"Creating empty dictionary")
    return data_dict



def dict_to_csv(csv_file_path, data_dict):
    import csv
    with open(csv_file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(data_dict.keys())  # Write header row
        writer.writerows(zip(*data_dict.values()))  # Write data rows