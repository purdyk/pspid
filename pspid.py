#!/usr/bin/env python

import re
import ConfigParser
import sys
import SabAPI
import NabAPI
import FileSpider

if __name__ == "__main__":

    dateMatcher = re.compile("(\d\d)?(\d\d)[^\d]?(\d\d)[^\d]?(\d\d)")

    config = ConfigParser.ConfigParser()
    config.read('pspid.conf')

    filespider = FileSpider.FileSpider(config, dateMatcher)
    sabapi = SabAPI.SabAPI(config)
    nabapi = NabAPI.NabAPI(config, dateMatcher)

    file_crit = sys.argv[1]
    search_crit = file_crit

    if len(sys.argv) > 2:
        search_crit += " " + sys.argv[2]

    have = filespider.build_file_list(file_crit)

    print "Have {0} files matching on disk".format(len(have))

    found = nabapi.do_search(search_crit)

    print "Found {0} results on the indexer".format(len(found))

    possible = filespider.filter_missing(have, found)

    ignored = filespider.load_ignored()

    for each in possible:
        if each.guid() not in ignored:
            nabapi.pretty_print(each)
            res = raw_input("\nEnqueue? [y/n/s/q] ")
            if res == 'y':
                sabapi.enqueue(each.link(), each.title())
            elif res == 's':
                print "skipping"
            elif res == 'q':
                break
            else:
                ignored.append(each['guid'])

    filespider.save_ignored(ignored)
