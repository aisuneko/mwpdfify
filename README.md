# mwpdfify
Batch download pages from MediaWiki sites (All pages or pages of a category) as printable PDFs. 

## Install / Run
`pip install mwpdfify`
...or clone repo and `pip install .` 
...or directly download and run `.py`

There are two PDF rendering backends to choose from: `pdfkit` (default) or `weasyprint`. Use `pip install -r requirements.txt` to install both or choose one yourself. If using the former remember to also install `wkhtmltopdf` on your system.

## Usage
1. Get the **full** address of `api.php` in desired wiki. Typically it should be directly under the site's root (like `/api.php`). For Wikipedia it's `/w/api.php`; tell me if there are any other exceptions ;)
2. (optional) If you want only a specific category, get its title (in the form of `Category:XXX`)
3. Run the script. eg.:
   - `mwpdfify https://lycoris-recoil.fandom.com/api.php` - Download all pages (as in Special:AllPages) from [Lycoris Recoil Fandom Wiki](https://lycoris-recoil.fandom.com/) as PDF
   - `mwpdfify https://wiki.archlinux.org/api.php -c Category:Installation_process` - Download all pages under Category:Installation_process from ArchWiki as PDF

The downloaded PDFs should be avaliable in a folder marked with the site's domain name in the current directory. 

See below for other parameters:
```
usage: mwpdfify [-h] [-c CATEGORY] [-p] [-t THREADS] [-l LIMIT] [-b BACKEND] url

positional arguments:
  url                   API (api.php) address of destination site

options:
  -h, --help            show this help message and exit
  -c CATEGORY, --category CATEGORY
                        Download only a specified category
  -p, --no-printable    Force normal instead of printable version of pages
  -t THREADS, --threads THREADS
                        Number of download threads, defaults to 8
  -l LIMIT, --limit LIMIT
                        Limit of JSON info returned at once, defaults to maximum (0)
  -b BACKEND, --backend BACKEND
                        PDF rendering backend to use, defaults to 'pdfkit'
```
## Known issues
- `&printable=yes` is deprecated in recent versions of MediaWiki (while no substitute API solutions are provided) so there might be layout issues when used with certain wikis; *especially* Fandom wikis as they also contain ads. 

## Changelog
- v1.0 (2022/09/03): Initial release

## License
LGPLv3
