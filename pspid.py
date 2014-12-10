#!/usr/bin/env python

import os
import re
import pickle
import ConfigParser
import sys
import SabAPI
import NabAPI

class PSpid:
    def __init__(self, matcher):
        self.matcher = matcher

    def build_file_list(self, matchSpec):
        glob_matcher = re.compile(".*" + matchSpec + ".*", re.I)
        file_list = {}
        for root, subs, files in os.walk(config.get('general', 'basedir')):
            for each in subs:
                if glob_matcher.match(each):
                    (d, fn) = self.build_tuple(self.matcher, each)
                    file_list[d] = (fn, '')

            for each in files:
                if glob_matcher.match(each):
                    (d1, fn) = self.build_tuple(self.matcher, each)
                    (d2, dirn) = self.build_tuple(self.matcher, root)
                    d = d1 if len(d1) > len(d2) else d2

                    file_list[d] = (dirn, fn)

        return file_list

    def build_tuple(self, matcher, filename):
        match = matcher.search(filename)
        if match:
            a = ".".join(match.groups()[-3:])
        else:
            a = ""
        return a, filename

    @staticmethod
    def filter_missing(have, found):
        possible = []
        for each in found.keys():
            if each not in have:
                possible.append(found[each])
        return possible

    @staticmethod
    def load_ignored():
        try:
            fh = open(os.path.expanduser("~/.pspid_ignored"))
            ignored = pickle.load(fh)
            fh.close
        except:
            ignored = []
        return ignored

    @staticmethod
    def save_ignored(ignored):
        fh = open(os.path.expanduser("~/.pspid_ignored"), "w")
        pickle.dump(ignored, fh)
        fh.close()

if __name__ == "__main__":

    dateMatcher = re.compile("(\d\d)?(\d\d)[^\d]?(\d\d)[^\d]?(\d\d)")

    config = ConfigParser.ConfigParser()
    config.read('pspid.conf')

    pspid = PSpid(dateMatcher)
    sabapi = SabAPI.SabAPI(config)
    nabapi = NabAPI.NabAPI(config, dateMatcher)

    file_crit = sys.argv[1]
    search_crit = file_crit

    if len(sys.argv) > 2:
        search_crit += " " + sys.argv[2]

    have = pspid.build_file_list(file_crit)

    print "Have {0} files matching on disk".format(len(have))

    found = nabapi.do_search(search_crit)

    print "Found {0} results on the indexer".format(len(found))

    possible = pspid.filter_missing(have, found)

    ignored = pspid.load_ignored()

    for each in possible:
        if each.guid() not in ignored:
            nabapi.pretty_print(each)
            res = raw_input("\nEnqueue? [y/n/s/q] ")
            if res == 'y':
                sabapi.enqueueReport(each.link(), each.title())
            elif res == 's':
                print "skipping"
            elif res == 'q':
                break;
            else:
                ignored.append(each['guid'])

    pspid.save_ignored(ignored)
