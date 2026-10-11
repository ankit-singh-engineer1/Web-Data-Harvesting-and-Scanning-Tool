import subprocess

def get_whois(url):
    print("Getting whois...")
    try:
        return subprocess.run(["whois", url], capture_output=True, text=True, timeout=60).stdout
    except Exception as e:
        return f"whois not available or failed: {e}"











# import os

# def get_whois(url):
#     command = "whois " + url
#     process = os.popen(command)
#     results = str(process.read()) 
#     print("Getting whois...")
#     return results