#!/usr/bin/env python

import os
import re
import pickle
import ConfigParser
import sys
import SabAPI
import NabAPI

class PSpid:
    def __init__(self):
        self.mb_b = 1048576

    def buildFileList(self, matchSpec):
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

    def buildTuple(self, matcher, thing):
        match = matcher.search(thing)
        if match:
            a = ".".join(match.groups()[-3:])
        else:
            a = ""
        return (a, thing)

    def filterMissing(self, have, found):
        possible = []
        for each in found.keys():
            if each not in have:
                possible.append(found[each])
        return possible

    def prettyPrint(self, thing):
        print "{0}\n\tSize: {1:0.0f} mb".format(thing['title'], float(thing['properAttr']['size']) / self.mb_b)

    def loadIgnored(self):
        try:
            fh = open(os.path.expanduser("~/.pspid_ignored"))
            ignored = pickle.load(fh)
            fh.close
        except:
            ignored = []
        return ignored

    def saveIgnored(self, ignored):
        fh = open(os.path.expanduser("~/.pspid_ignored"), "w")
        pickle.dump(ignored, fh)
        fh.close()

if __name__ == "__main__":

    dateMatcher = re.compile("(\d\d)?(\d\d)[^\d]?(\d\d)[^\d]?(\d\d)")

    config = ConfigParser.ConfigParser()
    config.read('pspid.conf')

    pspid = PSpid()
    sabapi = SabAPI.SabAPI(config)
    nabapi = NabAPI.NabAPI(config)
    nabapi.installFilter(dateMatcher)

    fileCrit = sys.argv[1]
    searchCrit = fileCrit

    if len(sys.argv) > 2:
        searchCrit += " " + sys.argv[2]
    have = pspid.buildFileList(fileCrit)

    print "Have {0} files matching on disk".format(len(have))

    found = nabapi.doSearch(searchCrit)

    print "Found {0} results on the indexer".format(len(found))

    possible = pspid.filterMissing(have, found)

    ignored = pspid.loadIgnored()

    for each in possible:
        if each['guid'] not in ignored:
            pspid.prettyPrint(each)
            res = raw_input("\nEnqueue? [y/n/s/q] ")
            if (res == 'y'):
                sabapi.enqueueReport(each['link'], each['title'])
            elif (res == 's'):
                print "skipping"
            elif (res == 'q'):
                break;
            else:
                ignored.append(each['guid'])

    pspid.saveIgnored(ignored)
