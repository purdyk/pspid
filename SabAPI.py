import urllib
import urllib2


class SabAPI:

    def __init__(self, config):
        self.config = config

    def enqueue(self, url, title):
        params = {
            "apikey": self.config.get('sabnzbd', 'key'),
            "mode": "addurl",
            "name": url,
            "cat": "xxx",
            "nzbname": title.replace(" ", "_")
            }
        finurl = self.config.get('sabnzbd', 'url') + urllib.urlencode(params)
        fh = urllib2.urlopen(finurl)
        print fh.read()
        fh.close()