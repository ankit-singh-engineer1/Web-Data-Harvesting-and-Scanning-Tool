import threading
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from link_finder import LinkFinder
from domain import *
from general import *

MAX_PAGES = 1000

class Spider:
    project_name = ''
    base_url = ''
    domain_name = ''
    queue_file = ''
    crawled_file = ''
    queue = set()
    crawled = set()
    shared_queue = None
    lock = threading.RLock()
    stopped = False

    def __init__(self, project_name, base_url, domain_name, thread_queue):
        Spider.stopped = False
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        Spider.shared_queue = thread_queue
        Spider.queue_file = Spider.project_name + '/queue.txt'
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        self.boot()
        for u in list(Spider.queue):  # resume pending links from a previous run
            thread_queue.put(u)
        self.crawl_page('First spider', Spider.base_url)

    @staticmethod
    def boot():
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)

    @staticmethod
    def crawl_page(thread_name, page_url):
        if Spider.stopped or len(Spider.crawled) >= MAX_PAGES or page_url in Spider.crawled:
            return
        links = Spider.gather_links(page_url)
        with Spider.lock:  # workers share these sets/files
            Spider.add_links_to_queue(links)
            Spider.queue.discard(page_url)
            Spider.crawled.add(page_url)
            Spider.update_files()

    @staticmethod
    def gather_links(page_url):
        html_string = ''
        try:
            # Use Request with headers to avoid being blocked
            req = Request(page_url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urlopen(req, timeout=10)
            if 'text/html' in (response.getheader('Content-Type') or ''):
                html_string = response.read().decode("utf-8", errors="ignore")
            finder = LinkFinder(Spider.base_url, response.geturl())  # final URL after redirects
            finder.feed(html_string)
        except Exception as e:
            print(f"Error gathering links from {page_url}: {str(e)}")
            return set()
        return finder.page_links()

    @staticmethod
    def canonical(url):
        # www.example.com and example.com count as the same host (the one the user typed)
        parts = urlparse(url)
        base_host = urlparse(Spider.base_url).netloc
        if parts.netloc.removeprefix('www.') == base_host.removeprefix('www.'):
            parts = parts._replace(netloc=base_host)
        return parts.geturl()

    @staticmethod
    def add_links_to_queue(links):
        for url in map(Spider.canonical, links):
            if (url in Spider.queue) or (url in Spider.crawled):
                continue
            if Spider.domain_name != get_domain_name(url):
                continue
            if len(Spider.crawled) + len(Spider.queue) >= MAX_PAGES:
                break
            
            Spider.queue.add(url)
            # Push to the thread-safe queue for workers to pick up
            if Spider.shared_queue:
                Spider.shared_queue.put(url)

    @staticmethod
    def update_files():
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file)


        

# from urllib.request import urlopen, Request
# from link_finder import LinkFinder
# from domain import *
# from general import *

# MAX_PAGES = 1000

# class Spider:
#     project_name = ''
#     base_url = ''
#     domain_name = ''
#     queue_file = ''
#     crawled_file = ''
#     queue = set()
#     crawled = set()
#     shared_queue = None

#     def __init__(self, project_name, base_url, domain_name, thread_queue):
#         Spider.project_name = project_name
#         Spider.base_url = base_url
#         Spider.domain_name = domain_name
#         Spider.shared_queue = thread_queue
#         Spider.queue_file = Spider.project_name + '/queue.txt'
#         Spider.crawled_file = Spider.project_name + '/crawled.txt'
#         self.boot()
#         self.crawl_page('First spider', Spider.base_url)

#     @staticmethod
#     def boot():
#         create_project_dir(Spider.project_name)
#         create_data_files(Spider.project_name, Spider.base_url)
#         Spider.queue = file_to_set(Spider.queue_file)
#         Spider.crawled = file_to_set(Spider.crawled_file)

#     @staticmethod
#     def crawl_page(thread_name, page_url):
#         if len(Spider.crawled) >= MAX_PAGES:
#             return
        
#         if page_url not in Spider.crawled:
#             Spider.add_links_to_queue(Spider.gather_links(page_url))
#             if page_url in Spider.queue:
#                 Spider.queue.remove(page_url)
#             Spider.crawled.add(page_url)
#             Spider.update_files()

#     @staticmethod
#     def gather_links(page_url):
#         html_string = ''
#         try:
#             # Use Request with headers to avoid being blocked
#             req = Request(page_url, headers={'User-Agent': 'Mozilla/5.0'})
#             response = urlopen(req)
#             if 'text/html' in response.getheader('Content-Type'):
#                 html_bytes = response.read()
#                 html_string = html_bytes.decode("utf-8")
#             finder = LinkFinder(Spider.base_url, page_url)
#             finder.feed(html_string)
#         except Exception as e:
#             print(f"Error gathering links from {page_url}: {str(e)}")
#             return set()
#         return finder.page_links()

#     @staticmethod
#     def add_links_to_queue(links):
#         for url in links:
#             if (url in Spider.queue) or (url in Spider.crawled):
#                 continue
#             if Spider.domain_name != get_domain_name(url):
#                 continue
#             if len(Spider.crawled) + len(Spider.queue) >= MAX_PAGES:
#                 break
            
#             Spider.queue.add(url)
#             # Push to the thread-safe queue for workers to pick up
#             if Spider.shared_queue:
#                 Spider.shared_queue.put(url)

#     @staticmethod
#     def update_files():
#         set_to_file(Spider.queue, Spider.queue_file)
#         set_to_file(Spider.crawled, Spider.crawled_file)