import subprocess
import json
import os

import logger

def execute(cmd):
    proc = subprocess.Popen(str(cmd), shell=True, stdout=subprocess.PIPE,)
    output = proc.communicate()[0].decode("utf-8")
    return output.split("\n")

def read_file(path):
    with open(str(path)) as file:
        content = file.readlines()
    content = [i.strip() for i in content]
    return content

def write_file(path, data):
    file = open(str(path), "w")
    for line in data:
        file.write(str(line) + "\n")
    file.close()

def read_json(path):
    with open(str(path)) as file:
        content = json.load(file)
    return content

def write_json(path, data):
    with open(str(path), "w") as file:
        json.dump(data, file, indent=4)

def create_file(path):
    file = open(str(path), "a+")
    file.close()

def get_id_files(id, dir_path):
    if os.path.exists(dir_path) == False or os.path.isdir(dir_path) == False:
        raise Exception(f"dir path {dir_path} does not exist!")
    files = []
    for f in os.listdir(dir_path):
        full_path = os.path.join(dir_path, f)
        if os.path.isfile(full_path) and (str(id) in f) and (".json" in full_path):
            files.append(full_path)
    return files

def delete_file(file_path):
    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
            logger.info(f"deleted file {file_path}")
        except Exception as err:
            logger.error(f"error! failed to delete file {file_path}")
    else:
        logger.info(f"file {file_path} does not exist")
