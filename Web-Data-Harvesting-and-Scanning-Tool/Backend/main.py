import sys                  # access to system-level parameters, like command-line arguments passed when running the script.
import threading            # Enables multi-threading so multiple tasks can run concurrently in the background.
from queue import Queue     # built-in thread-safe queue class to coordinate tasks safely across threads
from spider import Spider   # Imports your custom modules containing the core (e.g.; spider, domain, general)
from domain import *
from general import *

'''
In this project, we can do extra addition to make NUMBER_OF_THREADS and MAX_PAGES as variable (means user can provide in UI)

sys.argv is a list of strings representing everything typed. Suppose you typed it like below -- 
python main.py sample_project https://example.com
argv[0] -- main.py
argv[1] -- sample_project
argv[2] -- https://example.com
'''

if len(sys.argv) > 2:                # If arguments are >2 means project_name and home_page provided
    PROJECT_NAME = sys.argv[1]
    HOMEPAGE = sys.argv[2]
else:                                # if sys.argv<=2 then make a prompt (e.g; python main.py)
    PROJECT_NAME = input("Enter project name: ")
    HOMEPAGE = input("Enter homepage URL: ")

DOMAIN_NAME = get_domain_name(HOMEPAGE)    # Extracts the clean domain name (e.g., example.com) from your homepage URL.
QUEUE_FILE = PROJECT_NAME + '/queue.txt'    # Sets up the directory paths where text files will store pending and completed URLs on disk.
CRAWLED_FILE = PROJECT_NAME + '/crawled.txt'
NUMBER_OF_THREADS = 8                      # Defines how many concurrent background worker threads will be created.
queue = Queue()                            # Instantiates the master thread-safe queue that holds the to-do list of URLs(shared_queue).
Spider(PROJECT_NAME, HOMEPAGE, DOMAIN_NAME, queue) # Initializes the Spider class, passing down the project configurations and the shared queue.


# Create worker threads (will die when main exits)
def create_workers():                      
    for _ in range(NUMBER_OF_THREADS):   # Loops NUMBER_OF_THREADS times to spawn NUMBER_OF_THREADS independent background workers.
        t = threading.Thread(target=work)  # Creates a worker thread assigned to execute the work() function.
        t.daemon = True                  # Marks the thread as a daemon, meaning it will automatically shut down when your main program exits, preventing the script from hanging forever
        t.start()                        # Kicks off the thread so it begins running immediately in the background.

'''
If above t.daemon = False (The default): When your crawler finishes crawling all available pages, your main script reaches the end 
of the file. However, Python will refuse to shut down because it sees NUMBER_OF_THREADS background threads still alive and 
waiting inside that infinite loop. Your terminal will just freeze/hang, and you'll have to force-quit it (like pressing Ctrl + C).

url = queue.get() -- this blocks the thread if the queue is empty. The thread doesn't burn CPU cycles looping uselessly 
(which is called busy-waiting); it goes to sleep until another thread puts a new link into the queue. And yes, 
it grabs one URL at a time in a thread-safe manner (First-In, First-Out).
Every time a thread calls queue.get(), the queue increments an internal counter of "unfinished tasks." 
Calling queue.task_done() tells the queue, "I have finished processing that URL." This is especially important 
if your main script ever wants to call queue.join() to wait until every single queued link has been fully processed before shutting down.


When items are added (queue.put(link)): Every single time you put a link into the queue, Python's queue 
increases its internal counter by +1.
When workers finish items (queue.task_done()): Every time any worker thread finishes a URL and calls queue.task_done(), 
the internal counter decreases by -1.
What queue.join() does:
The thread running create_jobs() (usually the main thread) hits queue.join() and blocks (goes to sleep). 
It refuses to move forward until that internal counter reaches 0.
'''


# Do the next job in the queue
def work():
    while True:
        url = queue.get()            # Blocks (pauses) the thread until a new URL is dropped into the queue. Once available, it grabs it
        Spider.crawl_page(threading.current_thread().name, url) # download, parse, and extract links from that URL using the thread's name for identification
        queue.task_done()            # Signals to the queue that the current URL has finished processing.


# Each queued link is a new job
def create_jobs():
    for link in file_to_set(QUEUE_FILE):   # Reads from file on disk and place in python set
        queue.put(link)                    
    queue.join()               # powerful synchronization method provided by Python's Queue class. It blocks the thread running this function (typically the main thread) and waits until every single item placed in the queue has been processed and marked with queue.task_done().
    crawl()                    # Once queue.join() unblocks (meaning the queue is completely empty and all tasks are done), it calls the crawl() function.


# Check if there are items in the queue, if so crawl them
def crawl():
    queued_links = file_to_set(QUEUE_FILE)       # Reads the file from your disk and store in set queued_links
    if len(queued_links) > 0:
        print(str(len(queued_links)) + ' links in the queue')
        create_jobs()


create_workers()          # Spawns NUMBER_OF_THREADS background worker threads so they are up, running, and waiting for tasks.
crawl()                   # Triggers the initial scan of the queue file to load the homepage URL and start the entire crawling engine!


