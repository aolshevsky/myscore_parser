from myscore_parser import templates
import os
import json
import re


def save_to_json_file(data, file_name: str, project_dir: str):
    path_file = os.path.join(os.getcwd(), templates.base_dir,
                             project_dir, '{0}.json'.format(re.sub('[:|. ]', '_', file_name)))
    create_project_dir(project_dir)
    if not os.path.isfile(path_file):
        create_file(path_file)
    with open(path_file, 'w', encoding='utf-8') as outfile:
        json_str = json.dumps(data, ensure_ascii=False, indent=4)
        outfile.write(json_str)


def create_file(path: str):
    with open(path, 'w') as file:
        file.write('')


def create_project_dir(project_name: str):
    search_dir = os.path.join(templates.base_dir, project_name)
    if not os.path.exists(search_dir):
        os.makedirs(search_dir)


def is_file_in_project_dir(file_name: str, project_dir: str) -> bool:
    path_file = os.path.join(os.getcwd(), templates.base_dir,
                             project_dir, '{0}.json'.format(re.sub('[:|. ]', '_', file_name)))
    return os.path.isfile(path_file)


def save_data(data, file_name: str, project_dir: str):
    if not is_file_in_project_dir(file_name, project_dir):
        save_to_json_file(data, file_name, project_dir)


def load_data_from_json(file_name: str, project_dir: str):
    path_file = os.path.join(templates.base_dir, project_dir, file_name)
    with open(path_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data


def get_all_project_names(data_dir=templates.base_dir):
    for (_, dir_names, _) in os.walk(data_dir):
        return dir_names


def concat_project_files(project_name: str, file_names: list):
    data = []
    for f_name in file_names:
        if project_name not in ['match_events', 'teams']:
            if f_name.startswith('persons_Referee'):
                data.append(load_data_from_json(f_name, project_name))
            else:
                data += load_data_from_json(f_name, project_name)

        else:
            data.append(load_data_from_json(f_name, project_name))
    save_data(data, '_'.join(['all', project_name]), templates.base_db_dir)


def concat_data_files():
    create_project_dir(templates.base_db_dir)
    for project_name in get_all_project_names():
        if project_name == templates.base_db_dir:
            continue
        search_dir = os.path.join(templates.base_dir, project_name)
        files = []
        for (_, _, file_names) in os.walk(search_dir):
            files.extend(file_names)
            break
        concat_project_files(project_name, files)
