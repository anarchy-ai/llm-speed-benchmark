import json
import subprocess

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

