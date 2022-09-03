# This is a PoC script for downloading PDF of pages of a single category.
# It works by directly parsing links info on a wiki category page.
# If in case the target wiki's API (api.php) isn't available,
# try modifying and running the following code instead.
# Requires BeautifulSoup besides the dependencies specified in `setup.cfg`.

import re
import os
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import pdfkit
dir_path = os.path.join(os.getcwd(), 'artifacts')
try:
    os.mkdir(dir_path)
except FileExistsError:
    pass
os.chdir(dir_path)
# If the category page is truncated (eg. with 'next page' indicators) to multiple listings,
# go through ALL of them via the said links
# and fill their links one by one into this list (notice the 'pageuntil' and 'pagefrom' params):
html_pages = ["https://magireco.moe/index.php?title=Category:%E9%AD%94%E6%B3%95%E7%BA%AA%E5%BD%95%E4%B8%BB%E7%BA%BF%E5%89%A7%E6%83%85&pageuntil=%E4%B8%BB%E7%BA%BF%E5%89%A7%E6%83%85%2F%E7%AC%AC8%E7%AB%A0%2F43%E8%AF%9D#mw-pages",
              "https://magireco.moe/index.php?title=Category:%E9%AD%94%E6%B3%95%E7%BA%AA%E5%BD%95%E4%B8%BB%E7%BA%BF%E5%89%A7%E6%83%85&pagefrom=%E4%B8%BB%E7%BA%BF%E5%89%A7%E6%83%85%2F%E7%AC%AC8%E7%AB%A0%2F43%E8%AF%9D#mw-pages"]
pool = ThreadPoolExecutor(max_workers=10)
for page in html_pages:
    html = urllib.request.urlopen(page)
    soup = BeautifulSoup(html, "html.parser")
    for link in soup.select('div.mw-category li a'): # HTML element with links to category pages. May differ between wikis and can be viewed via F12
        link = urllib.parse.unquote(link.get('href'))
        name = re.escape(re.sub('/wiki/', '', link)) # used to retrieve title of page; format may differ between wikis and may require manual adjustment
        url = f"https://magireco.moe/index.php?title={name}&printable=yes" # replace the site domain with your wiki's
        #print(url)
        name = re.sub(r'/', '_', name)
        pool.submit(pdfkit.from_url, url, output_path=f'{name}.pdf')
        #print(f"completed {name}.pdf")

pool.shutdown(wait=True)
