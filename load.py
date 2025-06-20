import os
import json

def delete_file(path:str):
    if os.path.exists(path):
        os.remove(path)

def write_json(path:str, data:dict):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def get_json_data(path:str) -> dict | None:
    existing_data = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            existing_data = json.load(file)
    return  existing_data

def create_json_file(path:str, data:dict):
    with open(path, 'w', encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def convert_tweet_json_dict_to_list(path_input:str, path_output:str):
    if os.path.exists(path_input):
        with open(path_input, "r", encoding="utf-8") as file:
            existing_data = json.load(file)
        tweet_list = [{**v, "url": k} for k, v in existing_data.items()]
        create_json_file(path_output, tweet_list)

def merge_tweet_json(path_first:str, path_second:str, path_final:str) -> bool:
    if not os.path.exists(path_first) or not os.path.exists(path_second):
        return False

    first_data = get_json_data(path_first)
    second_data = get_json_data(path_second)

    for k, v in second_data.items():
        if k not in first_data: first_data[k] = {}
        for k_v, v_v in v.items():
            if isinstance(v_v, dict):
                first_data[k][k_v] = {}
                for k_k_v, v_v_V in v_v.items():
                    first_data[k][k_v][k_k_v] = v_v_V
            else:
                first_data[k][k_v] = v_v

    create_json_file(path_final, first_data)