__author__ = 'purdyk'
import os
import re
import pickle


class FileSpider:
    def __init__(self, config, matcher):
        self.matcher = matcher
        self.config = config

    def build_file_list(self, matchSpec):
        glob_matcher = re.compile(".*" + matchSpec + ".*", re.I)
        file_list = {}
        for root, subs, files in os.walk(self.config.get('general', 'basedir'), followlinks = True):
            for each in subs:
                if glob_matcher.match(each):
                    (d, fn) = self.build_tuple(each)
                    file_list[d] = (fn, '')

            for each in files:
                if glob_matcher.match(each):
                    (d1, fn) = self.build_tuple(each)
                    (d2, dirn) = self.build_tuple(root)
                    d = d1 if len(d1) > len(d2) else d2

                    file_list[d] = (dirn, fn)

        return file_list

    def build_tuple(self, filename):
        match = self.matcher.search(filename)
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
