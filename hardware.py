"""
Function for getting hardware information/metrics in python

All creidt for this code goes to Abdeladim Fadheli amazing article "How to Get Hardware and System Information in Python"

https://thepythoncode.com/article/get-hardware-system-information-python

November 20, 2023
"""

import psutil
import platform
from datetime import datetime
import GPUtil
from tabulate import tabulate
import subprocess
import sys
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
            key = tmp[0].lower().strip()
            value = tmp[1].strip()
            output[key] = value
    except:
        pass
    return output

########################################################################################

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

def system_info():
    uname = platform.uname()
    return {
        "platform": {
            "System": uname.system,
            "Node Name": uname.node,
            "Release": uname.release,
            "Version": uname.version,
            "Machine": uname.machine,
            "Processor": uname.processor
        },
        "neofetch": neofetch()
    }

def cpu_info(options={}):
    model_name = options.get("model")
    if model_name == None:
        model_name = neofetch()["cpu"]
    
    cores = None
    if options.get("cores") == True:
        cores = {}
        for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
            cores[str(i)] = f"{percentage}%"
    
    cpufreq = psutil.cpu_freq()

    output = {
        "model": str(model_name),
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
            "file_system_type": partition.fstype,
            "total_size": get_size(partition_usage.total),
            "used": get_size(partition_usage.used),
            "free": get_size(partition_usage.free),
            "usage": f"{partition_usage.percent}%",
            "partition_usage": partition_usage
        }
    
    disk_io = psutil.disk_io_counters()
    return {
        "total_read": get_size(disk_io.read_bytes),
        "total_write": get_size(disk_io.write_bytes),
        "partitions": output
    }

def gpu_info():
    gpus = GPUtil.getGPUs()
    gpus_data = {}
    for gpu in gpus:
        gpus_data[gpu.id] = {
            "raw": vars(gpu),
            "clean": {
                "id": gpu.id,
                "uuid": gpu.uuid,
                "name": gpu.name,
                "load": f"{gpu.load*100}%",
                "memory": {
                    "free": f"{gpu.memoryFree}MB",
                    "used": f"{gpu.memoryUsed}MB",
                    "total": f"{gpu.memoryTotal}MB"
                },
                "temp": f"{gpu.temperature} °C",

            }
        }
    return gpus_data


