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
