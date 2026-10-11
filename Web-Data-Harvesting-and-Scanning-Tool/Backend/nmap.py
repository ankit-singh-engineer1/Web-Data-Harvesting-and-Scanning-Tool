import subprocess

def get_nmap(options, ip):
    print("Getting nmap ...")
    try:
        return subprocess.run(["nmap", *options.split(), ip], capture_output=True, text=True, timeout=120).stdout
    except Exception as e:
        return f"nmap not available or failed: {e}"












# import os

# def get_nmap(options, ip):
#     command = "nmap " + options + " " + ip
#     process = os.popen(command)
#     results = str(process.read())
#     print("Getting nmap ...")
#     return results
