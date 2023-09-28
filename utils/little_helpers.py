
def return_sub_dict(whole_dict, filter_field_name, filter_value):
    #sub_dict = [value for value in whole_dict.values() if value[filter_field_name] == filter_value]
    sub_dict = {key: value for key, value in whole_dict.items() if value.get(filter_field_name) == filter_value}
    if not sub_dict:
        sub_dict = {}
    return sub_dict


def dict_to_txt(file_path, data_dict):
    with open(file_path, "w") as file:
        for key, value in data_dict.items():
            line = f"{key}: {value}\n"
            file.write(line)




def dict_to_csv(csv_file_path, data_dict):
    import csv
    with open(csv_file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(data_dict.keys())  # Write header row
        writer.writerows(zip(*data_dict.values()))  # Write data rows