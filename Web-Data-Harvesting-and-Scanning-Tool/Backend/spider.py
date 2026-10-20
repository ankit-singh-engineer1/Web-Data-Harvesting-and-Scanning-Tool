import threading                    #Module, which allows multiple threads to run concurrently
from urllib.parse import urlparse   # module to break down URLs into their component parts (scheme, domain, path, etc.) 
from urllib.request import urlopen, Request  # urlopen (to open and fetch web pages) and Request (to configure custom HTTP headers)
from link_finder import LinkFinder      # LinkFinder, designed to extract all hyperlinks (<a> tags) from an HTML page
from domain import *          # handles domain name extraction and validation 
from general import *         # Utility functions such as file I/O operations, directory creation, and set-to-file conversions

MAX_PAGES = 1000      # global constant integer setting a hard cap of 1,000 pages for the crawler to process, preventing infinite loops or runaway resource consumption.         

'''
LinkFinder is Microscopic (Single-Page):
It has zero awareness of the rest of the website, 
what files are on disk, or what other threads are doing. It is given a string of HTML, parses it, 
hands back a bucket of links, and its job for that page is done.

Spider & Worker Threads are Macroscopic (Site-Wide Orchestration):
The Spider acts as the manager. It takes those isolated buckets of links, normalizes them, 
filters out external domains, checks the queue and crawled sets to prevent duplicates, 
and hands them over to the shared_queue.

Multiple worker threads pull URLs out of that shared queue simultaneously. 
Thread 1 might be parsing the homepage, Thread 2 is crawling /about, 
and Thread 3 is crawling /store/item/42. They all feed new discoveries back into the same central system, 
updating files safely using locks.

'''

'''
@staticmethod is essentially a regular function that happens to live inside a class's namespace for organizational purposes
No self or cls: Unlike regular methods (which automatically receive self to access instance data) or class methods (which receive cls), 
a static method receives neither. 
Because it doesn't receive self, it cannot access or modify any instance-specific variables (self.variable).It is completely blind 
to which object called it but if multiple threads call it at the same time, you still need to handle locks or synchronization 
if the method modifies shared data or files.
Can be called without an instance: You can call it directly from the class itself (e.g., MyClass.boot()) without 
ever creating an object.


for url in map(Spider.canonical, links):
you can write above line like below also, above is just more pythonic way
for raw_link in links:
    url = Spider.canonical(raw_link)


Spider.queue (The Tracking Set) -- A standard Python set and its job is fast lookups and preventing duplicates. 
Sets are blazing fast at checking if something exists (url in Spider.queue). When a thread discovers 50 new links on a page, 
it needs to check instantly: "Have we already seen this link?" A set does this efficiently. 
However, a set has a downside: it is just a collection; it doesn't notify waiting threads when new items arrive.

Spider.shared_queue (The Task Dispatcher) -- A thread-safe queue.Queue from Python's built-in queue module. Distributing work to 
worker threads. In a multi-threaded program, worker threads need to know when there is a new URL to crawl. 
If the queue is empty, worker threads can call .get(), which puts them to sleep (blocking them) until a new item is .put() 
into the queue. This prevents your CPU from spinning at 100% searching for work. 

So, whenever a thread finds new links, it checks the Master Log (Spider.queue and Spider.crawled) 
to avoid duplicates, and then drops the unique new links into both the Master Log and the To-Do List (shared_queue) 
so workers can grab them.

'''


class Spider:   #this class encapsulates all the state and behavior of an individual web crawler worker
    project_name = ''     # From project_name to crawled_file, declares class-level attributes 
    base_url = ''         # initialized as empty strings. Because they belong to the class 
    domain_name = ''      # rather than instances, all spider threads share them.
    queue_file = ''
    crawled_file = ''
    queue = set()         # two class-level Python sets. queue holds URLs waiting to be crawled
    crawled = set()       # crawled tracks URLs that have already been visited. Sets ensure uniqueness and fast O(1) lookups.
    shared_queue = None   # Initializes a placeholder for a thread-safe queue object (like Python's queue.Queue) used to coordinate multiple worker threads.
    lock = threading.RLock()  # Creates a Reentrant Lock (RLock) to ensure that multiple threads can safely read and write to the shared sets and text files without data corruption or race conditions
    stopped = False         # flag used to signal all worker threads to stop execution immediately if required.

    def __init__(self, project_name, base_url, domain_name, thread_queue): # thread_queue in arguments because sharing the exact same "To-Do List" across multiple independent worker threads
        Spider.stopped = False       #assigns the passed constructor arguments to the class-level attributes. so all threads reference the same configuration
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        Spider.shared_queue = thread_queue
        Spider.queue_file = Spider.project_name + '/queue.txt'  #Constructs the file paths where the queue state and crawled history will be saved on disk inside the project folder
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        self.boot()              # boot() static method to initialize directories, create data files, and load any previously saved progress from disk.
        for u in list(Spider.queue):  # resume pending links from a previous run
            thread_queue.put(u)       #and pushes them into the live thread_queue so execution can resume seamlessly.
        self.crawl_page('First spider', Spider.base_url)  #Triggers the very first crawling task using the starting base_url

    @staticmethod       
    def boot():
        create_project_dir(Spider.project_name)    #general module to create the project directory 
        create_data_files(Spider.project_name, Spider.base_url)  # generate the initial queue and crawled text files if they don't already exist.
        Spider.queue = file_to_set(Spider.queue_file)      # Reads the text files from disk and populates the Spider.queue and Spider.crawled Python sets
        Spider.crawled = file_to_set(Spider.crawled_file)

    @staticmethod
    def crawl_page(thread_name, page_url):  #This function handles the core workflow of visiting a specific page URL.
        # print(f"[{thread_name}] Currently crawling: {page_url}")
        if Spider.stopped or len(Spider.crawled) >= MAX_PAGES or page_url in Spider.crawled: #if the stop flag is active, the maximum page limit has been reached, or the URL has already been crawled return.
            return
        links = Spider.gather_links(page_url)  # to fetch the webpage, parse its HTML content, and extract all outgoing links.
        with Spider.lock:                      # workers share these sets/files (Only one thread can execute this block at a time.)
            Spider.add_links_to_queue(links)   # Passes the newly discovered links to be filtered and added to the queue
            Spider.queue.discard(page_url)     # Safely removes the currently crawled URL from the waiting queue (using discard to avoid errors if it isn't present)
            Spider.crawled.add(page_url)       # Adds the processed URL to the crawled set to ensure it won't be visited again.
            Spider.update_files()              # Writes the updated sets back to their respective text files on disk for persistence

    @staticmethod
    def gather_links(page_url):
        html_string = ''          # Initializes an empty string for the HTML content
        try:                      # try...except block to catch network errors, timeouts, or bad responses safely
            # Use Request with headers to avoid being blocked 
            req = Request(page_url, headers={'User-Agent': 'Mozilla/5.0'}) # Creates an HTTP Request object equipped with a browser User-Agent header so the crawler isn't blocked by basic bot-detection filters
            response = urlopen(req, timeout=10)               # Sends the HTTP request over the network with a 10-second timeout limit        
            if 'text/html' in (response.getheader('Content-Type') or ''):  # Checks the response headers to ensure the server returned HTML content (handling potential None values safely with or '')
                html_string = response.read().decode("utf-8", errors="ignore")  # Reads the raw byte stream from the response and decodes it into a UTF-8 string, ignoring any invalid character decoding errors
            finder = LinkFinder(Spider.base_url, response.geturl())  # Instantiates the LinkFinder parser, passing the base URL and response.geturl() (which captures the final destination URL(single URL) if redirects occurred, that's why not page_url)
            finder.feed(html_string)     # Feeds the raw HTML string into the LinkFinder parser so it can locate and extract all hyperlinks
        except Exception as e:      # Catches any exceptions (like 404 errors, timeouts, or connection drops), prints an error message, and returns an empty set so the crawler doesn't crash
            print(f"Error gathering links from {page_url}: {e}")
            return set()
        return finder.page_links()    # Returns the set of links discovered by the LinkFinder

    @staticmethod
    def canonical(url):     # Declares a static helper method to normalize URLs
        # www.example.com and example.com count as the same host (the one the user typed)
        parts = urlparse(url)   # It will return named tuple for the page_url e.g.; ParseResult(scheme='https', netloc='www.example.com:8080', path='/path/to/page', params='', query='user=john', fragment='section2')
        base_host = urlparse(Spider.base_url).netloc   # Same for base_url and since it is named tuple we will be accessing it by dot.
        if parts.netloc.removeprefix('www.') == base_host.removeprefix('www.'):   # Removes both page_url and base_url "www." and compare
            parts = parts._replace(netloc=base_host)        # It will assign page_url to match base_url after stripping and Because tuples are immutable (read-only), you cannot assign you have to use _replace
        return parts.geturl()                               # Reconstructs and returns the normalized URL string.

    @staticmethod
    def add_links_to_queue(links):                 # Declares a static method that validates and registers newly discovered links
        for url in map(Spider.canonical, links):  # map(function, collection of items), It automatically takes every single item from that collection, passes it through the function one by one, and spits out the processed results.
            if (url in Spider.queue) or (url in Spider.crawled):      # checking if the URL is already crawled or queued
                continue
            if Spider.domain_name != get_domain_name(url):            # it stays within the same domain
                continue
            if len(Spider.crawled) + len(Spider.queue) >= MAX_PAGES:  # Enforcing the maximum page limit
                break
            
            Spider.queue.add(url)              # Add the URL in queue set (we have to put in both queue set and shared_queue queue)                      
            # Push to the thread-safe queue for workers to pick up
            if Spider.shared_queue:  # if a shared queue has been set up, go ahead and put the URL into it. If not, just skip this step safely.
                Spider.shared_queue.put(url)   # Python's built-in queue module (that's why using put and not add ) and for only 1 thread we don't need shared_queue 

    @staticmethod                    # static method for syncing in-memory set data to physical files on disk.
    def update_files():              # overwrite the queue and crawled text files with the current contents of their respective Python sets.
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file)


'''
Producer and consumer problem 
Locks 
Mutual exclusion

State Persistence & Crash Recovery
What It Does in Code : Reads/writes queue and crawled history via boot() and update_files().
The Interview Pitch (Short & Punchy) : Implements checkpointing. On startup, it loads historical state 
from disk to ensure durability and seamless resumption after crashes

Fault Tolerance & Exception Isolation
What It Does in Code : Wraps network requests, decoding, and parsing in try...except blocks with a 10s timeout.
The Interview Pitch (Short & Punchy) : Provides fault isolation. A 404 error or timeout on a single bad link 
is safely caught, preventing worker thread crashes.

Data Normalization & Deduplication
What It Does in Code : Uses canonical() to unify www variants and stores URLs in O(1) Python sets..
The Interview Pitch (Short & Punchy) : Treats the web as a graph, using canonicalization and set lookups 
to eliminate duplicate traversal and save bandwidth

Scope Bounding & Domain Isolation
What It Does in Code : Validates that target URLs match Spider.domain_name before queueing.
The Interview Pitch (Short & Punchy) : Enforces strict boundary control to prevent domain drift, 
stopping the crawler from accidentally scraping the rest of the web.

Anti-Bot Mitigation & Hygiene
What It Does in Code : Injects a custom browser User-Agent header (Mozilla/5.0) into HTTP requests.
The Interview Pitch (Short & Punchy) : Practices defensive networking, mimicking legitimate user traffic 
to bypass basic WAF and bot-detection blocks.

Separation of Concerns
What It Does in Code : Divides code responsibilities across LinkFinder, Spider, and I/O helpers.
The Interview Pitch (Short & Punchy) : Follows the Single Responsibility Principle, separating parsing, 
concurrency state management, and file I/O for clean maintainability.

----------------------------------------------------------------------------------------------------------

How to scale this single-machine multi-threaded crawler into a distributed multi-machine system?
To scale this crawler horizontally, I would transition from a single-node, thread-locked architecture 
to a distributed producer-consumer model.
1. I'd replace the local queue with a distributed message broker like Kafka to distribute workloads 
across worker nodes running in Kubernetes.

2. To solve the memory bottleneck for deduplication across millions of URLs, 
I'd implement Redis with Bloom Filters for ultra-fast, memory-efficient membership testing.

3. Finally, I'd introduce a distributed rate-limiter using Redis token buckets to ensure politeness and 
prevent target websites from blocking our IP pools.

'''