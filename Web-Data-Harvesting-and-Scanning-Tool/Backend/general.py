import os    #OS module, which allows the script to interact with the file system


# Each website is a separate project (folder)
def create_project_dir(directory):
    if not os.path.exists(directory):  #Checks if the folder already exists to prevent errors or overwriting existing folders.
        print('Creating directory ' + directory)
        os.makedirs(directory)    #Creates the directory (and any necessary parent directories) if it does not exist.

'''
OS	       Path separator	    Example code	                                Output
Windows	   \ (backslash)	    os.path.join("project", "data", "crawled.txt")	project\data\crawled.txt
Linux	   / (forward slash)	os.path.join("project", "data", "crawled.txt")	project/data/crawled.txt
macOS	   / (forward slash)	os.path.join("project", "data", "crawled.txt")	project/data/crawled.txt
'''

# Create queue and crawled files (if not created)
def create_data_files(project_name, base_url):
    queue = os.path.join(project_name , 'queue.txt')   
    crawled = os.path.join(project_name,"crawled.txt")
    if not os.path.isfile(queue):
        write_file(queue, base_url)
    if not os.path.isfile(crawled):
        write_file(crawled, '')


# Create a new file
def write_file(path, data): # create a new file (or completely overwrite an existing one) and write text data to it.
    with open(path, 'w') as f:  # with ensures the file is automatically closed when the block finishes.
        f.write(data)


# Add data onto an existing file
def append_to_file(path, data):
    with open(path, 'a') as file:  # Opens the file in append mode
        file.write(data + '\n')


# Delete the contents of a file
def delete_file_contents(path):
    open(path, 'w').close()  # Opens the file in write mode, which automatically truncates its contents, and immediately closes it using .close()


# Read a file and convert each line to set items
def file_to_set(file_name):
    results = set()                   # Initializes an empty Python set
    with open(file_name, 'rt') as f:  # Opens the file in read text mode
        for line in f:                # Python knows by "\n" that this line ends
            results.add(line.replace('\n', '')) #: Removes the invisible newline character ('\n') from the end of the line and adds the cleaned string into the set.
    return results


# Iterate through a set, each item will be a line in a file
def set_to_file(links, file_name):
    with open(file_name,"w") as f:  # Opens the target file in write mode
        for l in sorted(links):     # Sorts the set elements alphabetically and loops through each item l.
            f.write(l+"\n")         # Writes each link to the file followed by a newline character
