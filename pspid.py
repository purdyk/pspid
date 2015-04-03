#!/usr/bin/env python

import re
import ConfigParser
import sys
import SabAPI
import NabAPI
import FCSpider

if __name__ == "__main__":

    dateMatcher = re.compile("(\d\d)?(\d\d)[^\d]?(\d\d)[^\d]?(\d\d)")

    config = ConfigParser.ConfigParser()
    config.read('pspid.conf')

    spider = FCSpider.FileSpider(config, dateMatcher)
    sabapi = SabAPI.SabAPI(config)
    nabapi = NabAPI.NabAPI(config, dateMatcher)

    file_crit = sys.argv[1]
    search_crit = file_crit

    if len(sys.argv) > 2:
        search_crit += " " + sys.argv[2]

    have = spider.build_file_list(file_crit)

    print "Have {0} files matching on disk".format(len(have))

    #found is a dict key:date val:NabResult
    found = nabapi.do_search(search_crit)

    size_limit = int(config.get('general', 'minsize')) * 1048576

    filtered = {k:v for k,v in found.iteritems() if int(v.size()) >= size_limit}

    print "Found {0} / {1} results matching size constraint".format(len(found), len(filtered))

    possible = spider.filter_missing(have, filtered)

    ignored = spider.load_ignored()

    try:
        for each in possible:
            if each.guid() not in ignored:
                print each
                res = raw_input("\nEnqueue? [ (y)es / (n)o / (s)kip / (q)uit ] ")
                if res == 'y':
                    sabapi.enqueue(each.link(), each.title())
                elif res == 's':
                    print "skipping"
                elif res == 'q':
                    break
                else:
                    ignored.append(each.guid())

    except KeyboardInterrupt:
        print "\nexiting"

    finally:
        spider.save_ignored(ignored)
