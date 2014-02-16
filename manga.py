#!/usr/bin/python
__author__ = 'timur'

import urllib2
from BeautifulSoup import BeautifulSoup
import re
import os
import sys
import urlparse



def get_books(name, site):
    """
    Get list of book urls
    """
    print name
    url = urlparse.urljoin("http://"+site, name)
    if 'manga24' in site:
        try:
            print 'loading url: '+url
            page = urllib2.urlopen(url)
            html = page.read()
            try:
                parsedhtml = BeautifulSoup(html)
                ul = parsedhtml.findAll('ul', attrs={'class': 'all-chapters'})[0]
                atags = ul.findAll('a')
                links = ["http://manga24.ru/"+x['href'] for x in atags]
                return links
            except:
                try:
                    parsedhtml = BeautifulSoup(html)
                    a = parsedhtml.findAll('a', attrs={'class': 'button'})[0]
                    atags = (a,)
                    links = ["http://manga24.ru/"+x['href'] for x in atags]
                    return links
                except:
                    print "can't parse this shit"
                    sys.exit()
        except Exception:
            print "Wrong name... Or problem with internet connection.. or something"
            sys.exit()
    elif 'adultmanga.ru' in site:
        try:
            page = urllib2.urlopen(url)
            print "opening url: " + url
            html = page.read()
            try:
                parsedhtml = BeautifulSoup(html)
                div = parsedhtml.findAll('div', attrs={'class': 'subject-actions'})[0]
                atag = div.findAll('a')[-1]
                initial_page = atag['href']

                url = urlparse.urljoin("http://"+site, initial_page)
                print 'loading url: '+url
                page = urllib2.urlopen(url)
                html = page.read()
                try:
                    parsedhtml = BeautifulSoup(html)
                    sel = parsedhtml.findAll('select', attrs={'id': 'chapterSelectorSelect'})[0]
                    ops = sel.findAll('option')
                    links = [urlparse.urljoin("http://"+site, x['value']) for x in ops]
                    return links
                except:
                    print "can't find bookslist"
                    sys.exit()
            except:
                print "Can't find link"
                sys.exit()
        except Exception:
            print "Wrong name... Or problem with internet connection.. or something"
            sys.exit()
    else:
        print "Can't work with this site"
        sys.exit()



reg = r'"(.*)",.*,.*'
pattern_manga24 = re.compile(reg)
reg = r"url:\"(.*)\".*"
pattern_adultmanga = re.compile(reg)
def get_pages(book, site):
    """
    Get list of image urls returns (list, nameofbook)
    """
    if 'manga24.ru' in site:
        name =book.split('/')[-1]
        if(not name):
            name = book.split('/')[-2];
        try:
            page = urllib2.urlopen(book)
            html = page.read()
            try:
                parsedhtml = BeautifulSoup(html)
                js = parsedhtml.findAll('script')
                lines = js[2].text.split('\n')
                dir = lines[5].split(' ')[-1]
                files = ' '.join(lines[7].strip().split()[1:])
                dir = dir.replace('\/', '/')[1:-2]
                files = files[2:-2].split('], [')
                res_files = []
                for file in files:
                    match = pattern_manga24.match(file)
                    res_files.append(dir + match.group(1))
                return (res_files, name)
            except Exception as e:
                print e.message
                sys.exit()
        except Exception:
            print "Problem with internet connection, or something"
            sys.exit()
    elif 'adultmanga.ru' in site:
        name =book.split('/')[-1]
        name = book.split('/')[-2]+ "_" +name;
        pos = name.find('?')
        if pos >= 0:
            name = name[:pos]
        print name
        try:
            print book
            page = urllib2.urlopen(book)
            html = page.read()
            try:
                parsedhtml = BeautifulSoup(html)
                js = parsedhtml.findAll('script')
                lines = js[12].text.split('var')
                #dir = lines[3].split(' ')[-1]
                files = lines[2]
                pos = files.find('=')
                if pos >= 0:
                    files = files[pos+2:]
                    files = files.strip()[:-1]
                files = files[2:-2].split("},{")
                res_files = []
                for file in files:
                    match = pattern_adultmanga.match(file)
                    res_files.append(match.group(1))
                return (res_files, name)
            except Exception as e:
                print e.message
                sys.exit()
        except Exception:
            print "Problem with internet connection, or something"
            sys.exit()
    else:
        print "Can't work with this site"
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
        exist = False
        if not os.path.exists(os.path.join(name, book[1])):
            exist = True
            os.makedirs(os.path.join(name, book[1]))
        if exist and not rewrite:
            print "Downloading " + book[1]
            dirname = os.path.join(name, book[1])
            for page in book[0]:
                try:
                    urllib.urlretrieve(page, os.path.join(dirname, os.path.split(page)[-1]))
                except Exception as e:
                    print e.message
                    sys.exit()
        else:
            print "You already have "  + book[1]

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
-z           don't create cbz archives
-h (--help)  this help
"""

if __name__=="__main__":
    zip = False
    try:
        argv = sys.argv[1:]
        opts, args = getopt.getopt(argv, "hn:zr", ['help', 'name'])
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print helpmessage
                sys.exit()
            elif opt in ('-n', "--name"):
                splited_url = urlparse.urlparse(arg)
                site = splited_url[1]
                name = splited_url[2].split('/')[-1]
                if not name:
                    name = splited_url[2].split('/')[-2]
            elif opt == '-z':
                zip = True
            elif opt == "-r":
                rewrite = True
    except getopt.GetoptError:
        print helpmessage
        sys.exit(2)
    books = get_books(name, site)
    downloadable = []
    for book in books:
        downloadable.append(get_pages(book, site))
    download_files(downloadable, name)
    if (not zip):
        zipfiles(downloadable, name)
    print "Success!"