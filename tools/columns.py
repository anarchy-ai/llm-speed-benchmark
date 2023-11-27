import json
import os
import fnmatch

def read_json(path):
    with open(str(path)) as file:
        content = json.load(file)
    return content

def find_json_files(directory, deep_search=False):
    if deep_search == False:
        matches = []
        for file in os.listdir(directory):
            if file.endswith('.json'):
                matches.append(os.path.join(directory, file))
        return matches

    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, '*.json'):
            matches.append(os.path.join(root, filename))
    return matches

# main function calls

reports_path = os.path.join(os.path.abspath(os.path.join(os.getcwd(), os.pardir)), "reports")

json_files_paths = find_json_files(reports_path)

output = []
for path in json_files_paths:
    data = read_json(path)

    max_gpu_memory_usage = -1
    min_gpu_memory_usage = 1000000000000000000000000
    for key in list(data["metric"].keys()):
        # TODO: this currently only assumes the RAM usage is in MB, this needs to be fixed
        memory_usage = float(data["metric"][key]['gpu']['0']['memory']['used'].replace('MB', '')) / 1024
        if memory_usage > max_gpu_memory_usage:
            max_gpu_memory_usage = memory_usage
        if memory_usage < min_gpu_memory_usage:
            min_gpu_memory_usage = memory_usage

    tmp = {
        **data["test_env"]["params"],
        "runtime_sec": data["model"]["runtime_secs"],
        "tokens/sec": data["model"]["tokens_out/sec"],
        "tokens_in": data["model"]["tokens"]["input"],
        "tokens_out": data["model"]["tokens"]["output"],
        "gpu": data["metric"][list(data["metric"].keys())[0]]["gpu"]["0"]["name"],
        "max_gpu_memory_usage": max_gpu_memory_usage,
        "min_gpu_memory_usage": min_gpu_memory_usage,
        "file": path.split("/")[-1]
    }

    del tmp["prompt"]
    del tmp["model_start_pause"]
    del tmp["model_end_pause"]

    output.append(tmp)

print(json.dumps(output, indent=4))

