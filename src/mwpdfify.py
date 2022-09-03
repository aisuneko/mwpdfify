import re
import os
import json
import argparse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
try:
    import pdfkit
except ImportError:
    pdfkit = None
try:
    import weasyprint
except ImportError:
    weasyprint = None

def init_dir(name):
    dir_path = os.path.join(os.getcwd(), name)
    os.makedirs(name, exist_ok=True)
    os.chdir(dir_path)

def site_url(url, is_short):
    regex = r'^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/?\n]+)'
    if is_short:
        return re.findall(regex, url)[0]
    return re.match(regex, url)[0]

def get_pages(api_addr, limit, is_category, title, resume_pos):
    address = f"{api_addr}?action=query&format=json"
    limit = 'max' if not limit else limit
    if is_category:
        address = address + f"&list=categorymembers&cmtitle={title}&cmlimit={limit}"
    else:
        if resume_pos:
            address = address + f"&apcontinue={resume_pos}"
        address = address + f"&list=allpages&aplimit={limit}"
    response = urllib.request.urlopen(address)
    string = response.read().decode('utf-8')
    data = json.loads(string)
    return data

def weasyprint_write(url, name):
    pdf = weasyprint.HTML(url).write_pdf()
    with open(name, 'wb') as f:
        f.write(pdf)

def download(api, backend, threads=8, limit=None, title=None, noprintable=False):
    is_category = bool(title)
    with ThreadPoolExecutor(max_workers=threads) as pool:
        resume_pos = None
        futures = {}
        cnt = 0
        print(f"Using backend '{backend}'")
        notifier = f"Retrieving pages info of {site_url(api, True)}"
        if is_category:
            notifier = notifier + f" ({title})"
        print(notifier + "...")
        while True:
            data = get_pages(api, limit, is_category, title, resume_pos)
            if is_category:
                pages = data["query"]["categorymembers"]
            else:
                pages = data["query"]["allpages"]
            cnt = cnt + len(pages)
            for page in pages:
                name = page['title']
                siteurl = site_url(api, False)
                url = f"{siteurl}/index.php?title={name}"
                if not noprintable:
                    url = url + "&printable=yes"
                name = re.sub(r'/', '_', name)
                if backend == "pdfkit":
                    #options={'disable-javascript': None}
                    futures.update({pool.submit(pdfkit.from_url, url, output_path=f'{name}.pdf'): name})
                else:
                    futures.update({pool.submit(weasyprint_write, url, f'{name}.pdf'): name})
            if 'continue' not in data:
                break
            resume_pos = data['continue']['apcontinue']
        output(futures,cnt)

def output(futures, cnt):
    print(f"Found {cnt} pages to download")
    errcnt = 0
    curpos = 1
    for future in as_completed(futures):
        name = futures[future]
        try:
            _d = future.result()
        except Exception as e:
            print(f"({curpos}/{cnt}) ERROR on '{name}': {e}")
            errcnt = errcnt + 1
        else:
            print(f"({curpos}/{cnt}) Completed '{name}'")
        curpos = curpos + 1
    print(f"Done. {curpos-1} pages processed, {errcnt} errors")

def main():
    parser = argparse.ArgumentParser(description="Batch download printable PDF from MediaWiki sites")
    parser.add_argument('url', help='API (api.php) address of destination site')
    parser.add_argument('-c', '--category', help='Download only a specified category', type=str)
    parser.add_argument('-p', '--no-printable', help='Force normal instead of printable version of pages', action='store_true')
    parser.add_argument('-t', '--threads', help='Number of download threads, defaults to %(default)s', type=int, default=8)
    parser.add_argument('-l', '--limit', help='Limit of JSON info returned at once, defaults to maximum (%(default)s)', type=int, default=0)
    parser.add_argument('-b', '--backend', help='PDF rendering backend to use, defaults to \'%(default)s\'', type=str, default="pdfkit")

    args = parser.parse_args()
    folder_name = site_url(args.url, True)

    if (args.backend == "pdfkit" and not pdfkit) or (args.backend == "weasyprint" and not weasyprint):
        print(f"Backend '{args.backend}' unavailable; please install it first or switch to another")
        exit(0)
    if args.category:
        folder_name = folder_name + f" ({re.sub(r':', '=', args.category)})"
    init_dir(folder_name)
    download(args.url, args.backend, args.threads, args.limit, args.category, args.no_printable)
if __name__ == '__main__':
    main()
