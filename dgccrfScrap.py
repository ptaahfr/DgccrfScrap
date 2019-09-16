import json
import requests
import os
from pyquery import PyQuery as pq

class Cache(object):
    
    __CACHE_FILENAME = 'dgccrf_cache.json'

    def __init__(self):
        self.__entries = dict()
        if os.path.exists(__class__.__CACHE_FILENAME):
            with open(__class__.__CACHE_FILENAME, 'r') as cacheFile:
                self.__entries = json.load(cacheFile)
                pass

            if not isinstance(self.__entries, dict):
                raise TypeError(self.__entries)

            pass
        pass

    def get(self, url):
        fullUrl = 'https://www.economie.gouv.fr%s' % url
        if fullUrl in self.__entries:
            return self.__entries[fullUrl]
        
        body = requests.get(fullUrl).text
        self.__entries[fullUrl] = body

        with open(__class__.__CACHE_FILENAME, 'w') as cacheFile:
            json.dump(self.__entries, cacheFile, indent=4)
            pass

        return body

cache = Cache()

def parse_item(url, date):
    print('Processing: %s - %s' % (date, url))

    itemParser = pq(cache.get(url))
    content = itemParser('div .node__content').text()
    resultDict = { 'Date': date }

    for line in content.split('\n'):
        tokens = line.split(':')
        if len(tokens) >= 2:
            resultDict[tokens[0].strip()] = tokens[1].strip()
            pass

        pass
    
    return resultDict

import datetime

def parse_index(extract, url='/dgccrf/securite/archives-avis-rappels-de-produits', recurse=True):
    docParser  = pq(cache.get(url))

    def parse_content_item(selector):
        for linkDate in docParser(selector):
            try:
                dateStr = pq(linkDate).text().split(' ')[0].strip()
                # Parse to make sure we are on a valid item
                datetime.datetime.strptime(dateStr, '%d/%m/%Y')
                link = pq(linkDate)('a')
                linkParser = pq(link)
                extract.append(parse_item(linkParser.attr.href, dateStr))
            except:
                pass
            pass

    parse_content_item('div .content p')
    parse_content_item('div .content strong')

    if recurse:
        for link in docParser('div .inner2 li a'):
            linkParser = pq(link)
            extract = parse_index(extract, linkParser.attr.href, False)
            pass
        pass

    return extract

if __name__ == "__main__":
    extract = parse_index([])

    with open('dgccrf_rappels.json', 'w') as outfile:
        json.dump(extract, outfile, indent=4)

    pass