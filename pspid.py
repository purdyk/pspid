#!/usr/bin/env python

import os
import re
import urllib
import urllib2
import json
import pickle
import ConfigParser

mb_b = 1048576

dateMatcher = re.compile("(\d\d)?(\d\d)[^\d]?(\d\d)[^\d]?(\d\d)")

config = ConfigParser.ConfigParser()
config.read('pspid.conf')

def buildFileList(matchSpec):
    globMatcher = re.compile(".*" + matchSpec + ".*", re.I)
    fileList = {}
    for root, subs, files in os.walk(config.get('general', 'basedir')):
        for each in subs:
            if globMatcher.match(each):
                (d, fn) = buildTuple(dateMatcher,each)
                fileList[d] = (fn, '')

        for each in files:
            if globMatcher.match(each):
                (d1, fn) = buildTuple(dateMatcher,each)
                (d2, dirn) = buildTuple(dateMatcher,root)
                d = d1 if len(d1) > len(d2) else d2
                
                fileList[d] = (dirn, fn)
                        
    return fileList

def buildTuple(matcher, thing):
    match = matcher.search(thing)
    if match:
        a = ".".join(match.groups()[-3:])
    else:
        a = ""
    return (a, thing)

def doSearch(matchSpec):
    results = {}
    
    total = 1
    offset = 0

    while (total > offset):
        params = {
            "apikey":config.get('newznab','key'),
            "t":"search",
            "o":"json",
            "q":matchSpec,
            "cat":"6000",
            "offset": offset}
        finurl = config.get('newznab','url') + urllib.urlencode(params)
        #print "Fetching: ", finurl
        fh = urllib2.urlopen(finurl)
        data = json.load(fh)
        fh.close()

        total = int(data['channel']['response']['@attributes']['total'])
        if total > 0:
            raw = data['channel']['item']

            for thing in raw:
                if not type(thing) == type(dict()):
                    continue
                match = dateMatcher.search(thing['title'])
                if (match):
                    buildThingAttr(thing)
                    keep = True
                    key = ".".join(match.groups()[-3:])
            
                    if (key in results):
                        keep = int(results[key]['properAttr']['size']) < int(thing['properAttr']['size'])

                    if keep:
                        results[".".join(match.groups()[-3:])] = thing
         
            #Sends at most 100 results
            offset += 100
            
    return results

def filterMissing(have, found):
    possible = []
    for each in found.keys():
        if each not in have:
            possible.append(found[each])
    return possible

def buildThingAttr(thing):
    properAttr = {}
    for each in thing['attr']:
        properAttr[each['@attributes']['name']] = each['@attributes']['value']
    thing['properAttr'] = properAttr;

def prettyPrint(thing):
    print "{0}\n\tSize: {1:0.0f} mb".format(thing['title'], float(thing['properAttr']['size']) / mb_b)

def loadIgnored():
    try:
        fh = open(os.path.expanduser("~/.pspid_ignored"))
        ignored = pickle.load(fh)
        fh.close
    except:
        ignored = []
    return ignored

def saveIgnored(ignored):
    fh = open("/home/purdyk/.ss_ignored", "w")
    pickle.dump(ignored, fh)
    fh.close()

def enqueueReport(thing):
    params = {
        "apikey": config.get('sabnzbd', 'key'),
        "mode": "addurl",
        "name": thing['link'],
        "cat": "xxx",
        "nzbname": thing['title'].replace(" ", "_")
        }
    finurl = config.get('sabnzbd', 'url') + urllib.urlencode(params)
    fh = urllib2.urlopen(finurl)
    print fh.read()
    fh.close()
    

if __name__ == "__main__":
    import sys
    fileCrit = sys.argv[1]
    searchCrit = fileCrit
    if len(sys.argv) > 2:
        searchCrit += " " + sys.argv[2]
    have = buildFileList(fileCrit)

    print "Have {0} files matching on disk".format(len(have))

    found = doSearch(searchCrit)

    print "Found {0} results on the indexer".format(len(found))

    possible = filterMissing(have, found)

    ignored = loadIgnored()

    for each in possible:
        if each['guid'] not in ignored:
            prettyPrint(each)
            res = raw_input("\nEnqueue? [y/n/s/q] ")
            if (res == 'y'):
                enqueueReport(each)
            elif (res == 's'):
                print "skipping"
            elif (res == 'q'):
                break;
            else:
                ignored.append(each['guid'])

    saveIgnored(ignored)
