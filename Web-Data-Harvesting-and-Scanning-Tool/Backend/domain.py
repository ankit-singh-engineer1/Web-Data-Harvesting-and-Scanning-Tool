from urllib.parse import urlparse

'''
urlparse() function from the urllib.parse module breaks a URL string down into its fundamental building blocks. 
This is particularly useful for web scraping, URL manipulation, and routing.
urlparse(), splits URL into a 6-component structure: scheme, netloc, path, params, query, and fragment.
scheme - http, ftp, mailto, file, ws (WebSocket)
netloc - The domain name (or IP address) of the server, along with an optional port number or user credentials
url = "https://www.example.com:443/store/catalog/item;type=electronics?id=42&color=blue#reviews"
ParseResult(scheme='https', netloc='www.example.com:443', path='/store/catalog/item', params='type=electronics', query='id=42&color=blue', fragment='reviews')
'''


#Ensures the URL has a scheme so urlparse doesn't misinterpret domain names as paths.
def _normalize_url(url):
    if not url.startswith(('http://', 'https://', 'ftp://')):
        return 'http://' + url
    return url


# Get domain name (example.com)
def get_domain_name(url):
    try:
        results = get_sub_domain_name(url).split('.')  #Splits that string into a list of words separated by dots
        return results[-2] + '.' + results[-1]
    except:
        return ''


# Get sub domain name (name.example.com)
def get_sub_domain_name(url):
    try:
        url = _normalize_url(url)
        return urlparse(url).netloc   #netloc gives domain name (or IP address) of the server, along with an optional port number or user credentials
    except:
        return ''


# print(get_domain_name("http://www.youtube.com"))