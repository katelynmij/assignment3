import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
import pymongo

#initializing connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["web_crawler"]
pages_collection = db["pages"]

#url starts
frontier = ["https://www.cpp.edu/sci/computer-science/"]
visited = set()
target_found = False

def retrieveHTML(url):
    try:
        response = urllib.request.urlopen(url)
        return response.read()
    except Exception as e:
        print(f"Error retrieving {url}: {e}")
        return None
    
def parseHTML(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup

def storePage(url, html):
    pages_collection._insert_one({"url": url, "html": html})

def target_page(soup):
    #check if permanent faculty is there
    return bool(soup.find("h1", class_="cpp-h1", string="Permanent Faculty"))

def crawl():
    global target_found
    while frontier and not target_found:
        url = frontier.pop(0)
        if url in visited:
            continue

        visited.add(url)
        html = retrieveHTML(url)
        if not html:
            continue

        storePage(url, html)
        soup = parseHTML(html)

        if target_page(soup):
            print(f"Target page found: {url}")
            target_found = True
            break

        for link in soup.find_all("a", href=True):
            next_url = link["href"]
            if not next_url.startswith("http"):
                next_url = urllib.parse.urljoin(url, next_url)
            if next_url not in visited and next_url.endswith((".html", ".shtml")):
                frontier.append(next_url)

if __name__ == "__main__":
    crawl()