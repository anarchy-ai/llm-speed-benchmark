import subprocess
import os

def execute(cmd):
    proc = subprocess.Popen(str(cmd), shell=True, stdout=subprocess.PIPE,)
    output = proc.communicate()[0].decode("utf-8")
    return output.split("\n")

def getLLMVMLatestCommit():
    current_path = os.path.join(os.getcwd(), "LLM-VM")
    cmd = "git -C {} log | head -n 1 | awk '{{print $2}}'".format(current_path)
    output = execute(cmd)
    if len(output) == 0:
        return ""
    return output[0]

