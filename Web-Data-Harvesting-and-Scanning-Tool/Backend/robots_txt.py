import urllib.request  #Python’s built-in library for opening and reading URLs (making HTTP requests).
import io    # Handles core I/O operations. It is used here to safely decode raw binary HTTP response data into readable text.

def get_robots_txt(url):   #If the provided URL doesn't ends with a slash (/), it appends one to ensure standard formatting.
    if url.endswith('/'):
        path = url
    else:
        path = url + '/'
    
    try:
        # Adding User-Agent to prevent 403 Forbidden errors
        req = urllib.request.Request(path + "robots.txt", headers={'User-Agent': 'Mozilla/5.0'})  #Creates an HTTP request object that lets you attach custom headers
        with urllib.request.urlopen(req) as response:    #Sends the HTTP GET request to fetch the file.
            data = io.TextIOWrapper(response, encoding='utf-8')  #Takes raw byte stream from the server and decodes it. So, Python can read it as a standard string.
            return data.read()
    except Exception as e:
        return f"Could not retrieve robots.txt: {str(e)}"


# print(get_robots_txt("https://www.google.com")[:300])   #Prints the first 300 characters of result