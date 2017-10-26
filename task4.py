import sys
import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse
from urllib.parse import urljoin
import socket

url = sys.argv[1]
N = int(sys.argv[2])

inner_links = set()
outer_links = set()


def process(url):

    if ".pdf" in url:
        print("Skipping pdf...")
        return set(), set()

    local = set()
    remote = set()

    root_domain = urlparse(url).netloc
    try:
        root_ip = socket.gethostbyname(root_domain)
    except socket.gaierror:
        print("Unknown host: ", root_domain)
        print("Skipping...")
        return set(), set()
    print(url, " at ", root_ip)

    try:
        soup = bs(requests.get(url).content, "lxml")
    except:
        print("Timeout Error")
        print("Skipping...")
        return set(), set()

    for a in soup.find_all('a'):
        href = a.get('href')
        link = urljoin(url, href)
        if "mailto:" not in link:
            try:
                ip = socket.gethostbyname(urlparse(link).netloc)
            except socket.gaierror:
                print("Unknown host: ", urlparse(link).netloc)
                print("Skipping...")
                continue
            if ip == root_ip:
                local.add(link)
            else:
                remote.add(link)
    return local, remote


local, remote = process(url)

to_process = local - inner_links

inner_links = inner_links | local
outer_links = outer_links | remote


for i in range(0, N+1):
    copy = inner_links
    for l in to_process:
        local, remote = process(l)
        inner_links = inner_links | local
        outer_links = outer_links | remote
    to_process = inner_links - copy

outer_f = open("outer.txt", "w")
inner_f = open("inner.txt", "w")

for link in inner_links:
    print(link, file=inner_f)

for link in outer_links:
    print(link, file=outer_f)

outer_f.close()
inner_f.close()