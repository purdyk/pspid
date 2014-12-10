import urllib
import urllib2
import json

class NabAPI:
    def __init__(self, config):
        self.config = config

    def installFilter(self, filter):
        self.filter = filter

    def doSearch(self, matchSpec):
        results = {}

        total = 1
        offset = 0

        while (total > offset):
            params = {
                "apikey":self.config.get('newznab','key'),
                "t":"search",
                "o":"json",
                "q":matchSpec,
                "cat":"6000",
                "offset": offset}
            finurl = self.config.get('newznab','url') + urllib.urlencode(params)
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
                    match = self.filter.search(thing['title'])
                    if (match):
                        self.buildThingAttr(thing)
                        keep = True
                        key = ".".join(match.groups()[-3:])

                        if (key in results):
                            keep = int(results[key]['properAttr']['size']) < int(thing['properAttr']['size'])

                        if keep:
                            results[".".join(match.groups()[-3:])] = thing

                #Sends at most 100 results
                offset += 100

        return results

    def buildThingAttr(self, thing):
        properAttr = {}
        for each in thing['attr']:
            properAttr[each['@attributes']['name']] = each['@attributes']['value']
        thing['properAttr'] = properAttr;