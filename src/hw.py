"""
Function for getting hardware information/metrics in python

Massive credit goes to Abdeladim Fadheli's amazing article "How to Get Hardware and System Information in Python"
The following functions where based off of Fadheli's article:
    get_size()
    system_info()
    cpu_info()
    memory_info()
    disk_info()
    gpu_info()

https://thepythoncode.com/article/get-hardware-system-information-python

November 20, 2023
"""

import subprocess
import psutil
import platform
import GPUtil
import json

def execute(cmd):
    proc = subprocess.Popen(str(cmd), shell=True, stdout=subprocess.PIPE,)
    output = proc.communicate()[0].decode("utf-8")
    return output.split("\n")

def neofetch():
    # requires neofetch (https://github.com/dylanaraps/neofetch)
    cmd = "neofetch --stdout"
    output = {}
    try:
        stdout = execute(cmd)
        for line in stdout:
            if ": " not in line:
                continue
            tmp = line.split(": ", 1)
            if len(tmp) != 2:
                continue
            key = tmp[0].lower().strip().replace(" ", "")
            value = tmp[1].strip()
            output[key] = value
    except:
        pass
    return output

def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def system_info(native=True):
    if native == False:
        return neofetch()

    uname = platform.uname()
    return {
        "system": uname.system,
        "node_name": uname.node,
        "release": uname.release,
        "version": uname.version,
        "machine": uname.machine,
        "processor": uname.processor
    }

def cpu_info(options={}):
    # model_name = options.get("model")
    # if model_name == None:
    #     model_name = neofetch()["cpu"]
    
    cores = None
    if options.get("cores") == True:
        cores = {}
        for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
            cores[str(i)] = f"{percentage}%"
    
    cpufreq = psutil.cpu_freq()

    output = {
        # "model": str(model_name),
        "physical_cores": psutil.cpu_count(logical=False),
        "total_cores": psutil.cpu_count(logical=True),
        "max_frequency": f"{cpufreq.max:.2f}Mhz",
        "min_frequency": f"{cpufreq.min:.2f}Mhz",
        "current_frequency": f"{cpufreq.current:.2f}Mhz"
    }

    if cores != None:
        output["cores"] = cores

    return output

def memory_info():
    svmem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "total": get_size(svmem.total),
        "available": get_size(svmem.available),
        "used": get_size(svmem.used),
        "percentage": svmem.percent,
        "swap": {
            "total": get_size(swap.total),
            "free": get_size(swap.free),
            "used": get_size(swap.used),
            "usage": swap.percent
        }
    }

def disk_info():
    output = {}
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            partition_usage = ""

        output["partition.device"] = {
            "mount_point": partition.mountpoint,
            "file_system_type": partition.fstype
        }

        if partition_usage != "":
            output["partition.device"] = {**output["partition.device"], **{
                "total_size": get_size(partition_usage.total),
                "used": get_size(partition_usage.used),
                "free": get_size(partition_usage.free),
                "usage": f"{partition_usage.percent}%"
            }}
    
    disk_io = psutil.disk_io_counters()
    return {
        "total_read": get_size(disk_io.read_bytes),
        "total_write": get_size(disk_io.write_bytes),
        "partitions": output
    }

def gpu_info(raw=False):
    gpus = GPUtil.getGPUs()
    gpus_data = {}
    for gpu in gpus:
        if raw:
            gpus_data[gpu.id] = vars(gpu)
        else:
            gpus_data[gpu.id] = {
                "id": gpu.id,
                "uuid": gpu.uuid,
                "name": gpu.name,
                "driver": gpu.driver,
                "load": f"{gpu.load*100}%",
                "memory": {
                    "free": f"{gpu.memoryFree}MB",
                    "used": f"{gpu.memoryUsed}MB",
                    "total": f"{gpu.memoryTotal}MB"
                },
                "temp": f"{gpu.temperature} °C"
            }
    return gpus_data

def get_all(static_only=False):
    if static_only:
        return {
            "system": system_info(),
            "neofetch": system_info(False)
        }
    
    return {
        "cpu": cpu_info({"cores": True}),
        "ram": memory_info(),
        "disk": disk_info(),
        "gpu": gpu_info()
    }
