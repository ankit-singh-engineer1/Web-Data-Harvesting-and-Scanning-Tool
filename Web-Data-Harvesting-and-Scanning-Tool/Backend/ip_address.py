import socket   #module to communicate over network protocols and interact with OS networking APIs.

def get_ip_address(url):            # takes hostname "www" or domain name "google.com"
    print("Getting IP address ...")
    try:
        return socket.gethostbyname(url) #queries system's DNS resolver to convert the domain name into an IPv4 string
    except Exception as e:       #Catches errors that occur during the lookup (host is invalid or internet connection is down)
        return f"Could not resolve {url}: {e}"

# print(get_ip_address("www.google.com"))