import urllib
import urllib2
import json


class NabAPI:
    def __init__(self, config, filter_re):
        self.config = config
        self.filter = filter_re

    def do_search(self, match_spec):
        results = {}

        total = 1
        offset = 0

        while total > offset:
            params = {
                "apikey": self.config.get('newznab', 'key'),
                "t": "search",
                "o": "json",
                "q": match_spec,
                "cat": "6000",
                "offset": offset}
            finurl = self.config.get('newznab', 'url') + urllib.urlencode(params)
            # print "Fetching: ", finurl
            fh = urllib2.urlopen(finurl)
            data = json.load(fh)
            fh.close()

            total = int(data['channel']['response']['@attributes']['total'])
            if total > 0:
                raw = data['channel']['item']

                for thing in raw:
                    if not type(thing) == type(dict()):
                        continue

                    result = NabResult(thing)

                    match = self.filter.search(result.title())

                    if match:
                        keep = True
                        key = ".".join(match.groups()[-3:])

                        if key in results:
                            keep = int(results[key].size()) < int(result.size())

                        if keep:
                            results[".".join(match.groups()[-3:])] = result

                # Sends at most 100 results
                offset += 100

        return results

class NabResult:
    mb_b = 1048576

    def __init__(self, attrs):
        self.attrs = attrs
        self.build_attrs()

    def build_attrs(self):
        _attrs = {}
        for each in self.attrs['attr']:
            _attrs[each['@attributes']['name']] = each['@attributes']['value']
        self.attrs['_attrs'] = _attrs

    def size(self):
        return self.attrs['_attrs']['size']

    def title(self):
        return self.attrs['title']

    def guid(self):
        return self.attrs['guid']

    def link(self):
        return self.attrs['link']

    def __str__(self):
        return "{0}\n\tSize: {1:0.0f} mb".format(self.title(), float(self.size()) / NabResult.mb_b)
