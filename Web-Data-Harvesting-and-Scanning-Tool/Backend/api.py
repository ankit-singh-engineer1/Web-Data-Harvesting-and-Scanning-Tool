from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from spider import Spider
from domain import *
from ip_address import get_ip_address
from nmap import get_nmap
from robots_txt import get_robots_txt
from whois import get_whois
from queue import Queue
import threading

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class CrawlRequest(BaseModel):
    url: str

site_intel = {
    "ip": "Analyzing...",
    "nmap": "Scanning...",
    "whois": "Retrieving...",
    "robots": "Checking..."
}

task_queue = Queue()
workers_started = False

# def run_recon(url):
#     global site_intel
#     try:
#         domain = get_domain_name(url)
#         site_intel["ip"] = get_ip_address(domain)
#         site_intel["nmap"] = get_nmap("-F", site_intel["ip"])
#         site_intel["whois"] = get_whois(domain)
#         site_intel["robots"] = get_robots_txt(url)
#     except:
#         pass

#new
def run_recon(url):
    global site_intel
    try:
        domain = get_domain_name(url)
        site_intel["ip"] = get_ip_address(domain)
        site_intel["nmap"] = get_nmap("-F", site_intel["ip"])
        site_intel["whois"] = get_whois(domain)
        # Capture robots.txt output correctly
        site_intel["robots"] = get_robots_txt(url)
    except Exception as e:
        site_intel["robots"] = f"Error: {str(e)}"

def work():
    while True:
        url = task_queue.get()
        try:
            Spider.crawl_page(threading.current_thread().name, url)
        except Exception as e:
            print(f"Worker error on {url}: {e}")
        finally:
            task_queue.task_done()

def start_workers():
    global workers_started
    if not workers_started:
        for _ in range(8):
            t = threading.Thread(target=work)
            t.daemon = True
            t.start()
        workers_started = True

@app.post("/crawl")
async def start_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    domain = get_domain_name(request.url)
    project_name = domain.replace('.', '_')
    
    start_workers()
    background_tasks.add_task(run_recon, request.url)
    background_tasks.add_task(Spider, project_name, request.url, domain, task_queue)
    
    return {"message": "Crawler and Recon started"}

def _domain(url):
    d = get_domain_name(url)
    if not d:
        raise HTTPException(status_code=400, detail="Invalid URL (include http:// or https://)")
    return d

@app.get("/ip")
def ip_endpoint(url: str):
    return {"ip": get_ip_address(_domain(url))}

@app.get("/whois")
def whois_endpoint(url: str):
    return {"whois": get_whois(_domain(url))}

@app.get("/nmap")
def nmap_endpoint(url: str):
    return {"nmap": get_nmap("-F", get_ip_address(_domain(url)))}

@app.get("/robots")
def robots_endpoint(url: str):
    return {"robots": get_robots_txt(url)}

@app.get("/links")
def links_endpoint():
    return {"crawled": sorted(Spider.crawled), "queue": sorted(Spider.queue)}

@app.get("/status")
async def get_status():
    total = len(Spider.crawled) + len(Spider.queue)
    success_rate = 0
    if total > 0:
        success_rate = round((len(Spider.crawled) / total) * 100)
    
    return {
        "links": list(Spider.crawled),
        "queue_count": len(Spider.queue),
        "crawled_count": len(Spider.crawled),
        "success_rate": success_rate,
        "intel": site_intel
    }





# from fastapi import FastAPI, BackgroundTasks
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from spider import Spider
# from domain import *
# from ip_address import get_ip_address
# from nmap import get_nmap
# from robots_txt import get_robots_txt
# from whois import get_whois
# from queue import Queue
# import threading

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class CrawlRequest(BaseModel):
#     url: str

# site_intel = {
#     "ip": "Analyzing...",
#     "nmap": "Scanning...",
#     "whois": "Retrieving...",
#     "robots": "Checking..."
# }

# task_queue = Queue()
# workers_started = False

# # def run_recon(url):
# #     global site_intel
# #     try:
# #         domain = get_domain_name(url)
# #         site_intel["ip"] = get_ip_address(domain)
# #         site_intel["nmap"] = get_nmap("-F", site_intel["ip"])
# #         site_intel["whois"] = get_whois(domain)
# #         site_intel["robots"] = get_robots_txt(url)
# #     except:
# #         pass

# #new
# def run_recon(url):
#     global site_intel
#     try:
#         domain = get_domain_name(url)
#         site_intel["ip"] = get_ip_address(domain)
#         site_intel["nmap"] = get_nmap("-F", site_intel["ip"])
#         site_intel["whois"] = get_whois(domain)
#         # Capture robots.txt output correctly
#         site_intel["robots"] = get_robots_txt(url)
#     except Exception as e:
#         site_intel["robots"] = f"Error: {str(e)}"

# def work():
#     while True:
#         url = task_queue.get()
#         Spider.crawl_page(threading.current_thread().name, url)
#         task_queue.task_done()

# def start_workers():
#     global workers_started
#     if not workers_started:
#         for _ in range(8):
#             t = threading.Thread(target=work)
#             t.daemon = True
#             t.start()
#         workers_started = True

# @app.post("/crawl")
# async def start_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
#     domain = get_domain_name(request.url)
#     project_name = domain.replace('.', '_')
    
#     start_workers()
#     background_tasks.add_task(run_recon, request.url)
#     background_tasks.add_task(Spider, project_name, request.url, domain, task_queue)
    
#     return {"message": "Crawler and Recon started"}

# @app.get("/status")
# async def get_status():
#     total = len(Spider.crawled) + len(Spider.queue)
#     success_rate = 0
#     if total > 0:
#         success_rate = round((len(Spider.crawled) / total) * 100)
    
#     return {
#         "links": list(Spider.crawled),
#         "queue_count": len(Spider.queue),
#         "crawled_count": len(Spider.crawled),
#         "success_rate": success_rate,
#         "intel": site_intel
#     }