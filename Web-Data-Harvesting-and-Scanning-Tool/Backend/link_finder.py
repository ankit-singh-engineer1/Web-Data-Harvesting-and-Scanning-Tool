from html.parser import HTMLParser  # parsing HTML documents (handling tags, attributes etc.)
from urllib import parse            # Used to make HTTP requests and import URL manipulation tools

'''
LinkFinder is Microscopic (Single-Page):
It has zero awareness of the rest of the website, what files are on disk, 
or what other threads are doing. It is given a string of HTML, parses it, hands back a bucket of links, 
and its job for that page is done.

base_url is used later as a security fence to make sure your crawler stays inside the target website.
urljoin needs page_url to stitch relative paths together correctly based on folder depth.
In below in parse.urljoin if you give self.baseurl
Suppose your baseurl = https://example.com and your crawler moves away from the homepage 
and visits a deep blog post https://example.com/blog/tech/posts.html and Inside that posts.html page, 
the web developer wrote a relative link to another article like <a href="article-2.html"> then notice
there is no https://example.com/blog/tech/ but parse.urljoin("https://example.com", "article-2.html")
is we have if we use base_url which becomes https://example.com/article-2.html which is wrong.
That's why always use page_url so that, it always take correct URL because it resolves like below,
parse.urljoin("https://example.com/blog/tech/posts.html", "article-2.html") which gives 
https://example.com/blog/tech/article-2.html and Python correctly understands that article-2.html lives in that same folder, preserving the full path.
'''

class LinkFinder(HTMLParser):     # New class that inherits from HTMLParser
    #self is simply Python's standard way of referring to the exact object you just created.

    def __init__(self, base_url, page_url):   #Constructor method runs automatically when you create a new LinkFinder object
        super().__init__()                 #Initializes the parent HTMLParser class so its internal scanning engine is properly set up.
        self.base_url = base_url           #Stores the absolute root domain (used to keep your crawler inside the target website).
        self.page_url = page_url           #Stores the URL of the specific page being parsed right now.
        self.links = set()                 # Empty Python set to store discovered URLs

    # When we call HTMLParser feed() this function is called when it encounters an opening tag <a>
    def handle_starttag(self, tag, attrs):  # Built-in HTMLParser method that automatically triggers every single time the parser encounters an opening HTML tag (like <html>, <div>, <p>, or <a>).
        if tag == 'a':                        # attrs is a list of tuples containing the tag's attributes. Below is example
            for (attribute, value) in attrs:   # [('href', 'https://example.com'), ('class', 'nav-link')]
                if attribute == 'href':        # parse.urljoin(self.page_url, value): Converts relative links (like /contact or about.html) into absolute URLs based on the current page's URL.
                    url = parse.urldefrag(parse.urljoin(self.page_url, value))[0]  # parse.urldefrag(...)[0]: Strips out any internal anchor fragments (like #top or #section2 in a same page doesn't add as 2 URL's but as 1 URL only), keeping only the clean base URL string [0].
                    self.links.add(url)        #Adds the absolute URL into your self.links set.

    def page_links(self):      # Hands back the populated set of unique URLs
        return self.links

    def error(self, message):  #silently ignore syntax errors in web pages rather than crashing your web crawler when it hits messy HTML
        pass
