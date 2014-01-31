#!/usr/bin/python
__author__ = 'timur'

import urllib2
from BeautifulSoup import BeautifulSoup
import re
import os
import sys

def get_books(name):
    """
    Get list of book urls
    """
    url = "http://manga24.ru/"+name
    print 'loading url: '+url
    try:
        page = urllib2.urlopen(url)
        html = page.read()
        try:
            parsedhtml = BeautifulSoup(html)
            ul = parsedhtml.findAll('ul', attrs={'class': 'mlist'})[0]
            atags = ul.findAll('a')
            links = ["http://manga24.ru/"+x['href'] for x in atags]
            return links
        except:
            try:
                parsedhtml = BeautifulSoup(html)
                ul = parsedhtml.findAll('div', attrs={'class': 'item2'})[0]
                atags = ul.findAll('a')
                links = ["http://manga24.ru/"+x['href'] for x in atags]
                return links
            except:
                print "can't parse this shit"
                sys.exit()
    except Exception:
        print "Wrong name... Or problem with internet connection.. or something"
        sys.exit()




reg = r'"(.*)",.*,.*'
pattern = re.compile(reg)
def get_pages(book):
    """
    Get list of image urls returns (list, nameofbook)
    """
    name =book.split('/')[-1]
    if(not name):
        name = book.split('/')[-2];
    try:
        page = urllib2.urlopen(book)
        html = page.read()
        try:
            parsedhtml = BeautifulSoup(html)
            js = parsedhtml.findAll('script')
            lines = js[4].text.split('\n\t')
            dir = lines[3].split(' ')[-1]
            files = lines[5].split(' ')[-1]
            dir = dir.replace('\/', '/')[1:-2]
            files = files[2:-2].split('],[')
            res_files = []
            for file in files:
                match = pattern.match(file)
                res_files.append(dir + match.group(1))
            return (res_files, name)
        except Exception as e:
            print e.message
            sys.exit()
    except Exception:
        print "Problem with internet connection, or something"
        sys.exit()

def download_files (downloadable, name):
    """
    downloads files
    """
    print "downloading images"
    if not os.path.exists(name):
        os.makedirs(name)
    import urllib
    for book in downloadable:
        if not os.path.exists(os.path.join(name, book[1])):
            os.makedirs(os.path.join(name, book[1]))
        dirname = os.path.join(name, book[1])
        for page in book[0]:
            try:
                urllib.urlretrieve(page, os.path.join(dirname, os.path.split(page)[-1]))
            except Exception as e:
                print e.message
                sys.exit()

def zipfiles (downloadable, name):
    """
    creates cbz of books
    """

    print "compressing files. almost done."
    import zipfile
    for book in downloadable:
        if (os.path.exists(os.path.join(name, book[1]))):
            files = os.listdir(os.path.join(name, book[1]))
            cbz = zipfile.ZipFile(os.path.join(name, name + '-' + book[1] + '.cbz'), 'w')
            for file in files:
                cbz.write(os.path.join(name, book[1],file))
            cbz.close()

import getopt
helpmessage = """
-n (--name)  name of manga you want to download
-z           create cbz archives
-h (--help)  this help
"""

if __name__=="__main__":
    zip = False
    try:
        argv = sys.argv[1:]
        opts, args = getopt.getopt(argv, "hn:z", ['help', 'name'])
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print helpmessage
                sys.exit()
            elif opt in ('-n', "--name"):
                name = arg
            elif opt == '-z':
                zip = True

    except getopt.GetoptError:
        print helpmessage+ "!!!!"
        sys.exit(2)
    books = get_books(name)
    downloadable = []
    for book in books:
        downloadable.append(get_pages(book))
    download_files(downloadable, name)
    if (zip):
        zipfiles(downloadable, name)
    print "Success!"