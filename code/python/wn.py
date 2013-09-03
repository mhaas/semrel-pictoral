#!/usr/bin/python2
# -*- coding: utf-8 -*-

from nltk.corpus import wordnet as wn

def get_synset_from_id(synsetID):
    return wn.synset(synsetID.replace("'", ""))

def get_hypernyms(synset, max_depth = 99999):
    ret = []
    paths = synset.hypernym_paths()
    for path in paths:
        for hypernym in path:
            depth = hypernym.min_depth()
            if depth <= max_depth:
                ret.append((hypernym, depth))
    return ret
    

def get_synset(word, pos, sense):
    # fixup - basically port stuff from wordnet 1.6 to 3.1
    if (word == "iron" and pos == "n" and sense == "5"):
        sense = "4"
    if (word == "cymbals" and pos == "n" and sense == "1"):
        word = "cymbal"
    if (word == "pre season" or word == "pre_season"):
        word = "preseason"

    word = word.replace(" ", "_")
    identifier = "%s.%s.%s" % (word, pos, sense)
    print "looking up identifier: %s" % identifier
    return wn.synset(identifier)




 
