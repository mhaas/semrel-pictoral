#!/usr/bin/python2
# -*- coding: utf-8 -*-

import re
import wn

def read_data(fileName):

    fh = open(fileName, "r")
    data = []
    regex = re.compile("rel\((.*)\)")
    for foo in fh.readlines():
        data.append(regex.match(foo).group(1))
    data = map(lambda x: x.replace("[",""), data)
    data = map(lambda x: x.replace("]",""), data)
    for d in data:
        s = d.split(",")
        if s[2] == "n" and s[5] == "n":
            print s
    candidates = []
    for d in data:
        s = d.split(",")
        if s[2] == "n" and s[5] == "n":
            candidates.append(  {"firstWord" : clean(s[1]),
                                "firstWordPos": s[2],
                                "firstWordSense" : s[3],
                                "firstWordSynset" : wn.get_synset(clean(s[1]), s[2], s[3]),
                                "secondWord" : clean(s[4]),
                                "secondWordPos": s[5],
                                "secondWordSense": s[6],
                                "secondWordSynset" : wn.get_synset(clean(s[4]), s[5], s[6]),
                                "relation" : s[7] })
    return candidates
                                    
def clean(word):
    word = word.replace("'", "")
    print word
    return word
           
  
if __name__ == "__main__":
    read_data("/home/laga/uni/kurse/2013/ss/dist_semantik/hausarbeit/nmr_relations_5class.data")
