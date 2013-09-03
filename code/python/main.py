#!/usr/bin/python2
# -*- coding: utf-8 -*-

import wn
import data
import imgnet
import time

def main():
    dataFile = "/home/laga/uni/kurse/2013/ss/dist_semantik/hausarbeit/nmr_relations_5class.data"
    # only nounds
    words = data.read_data(dataFile)
    # build vocabulary
    vocab = set()
    concepts = set()
    for word in words:
        vocab.update(wn.get_hypernyms(word["firstWordSynset"], 7))
        concepts.add(word["firstWordSynset"])
        concepts.add(word["secondWordSynset"])
        vocab.update(wn.get_hypernyms(word["secondWordSynset"], 7))
    s = sorted(vocab)
    print s 
    indices = {}
    for x in range(0, len(s)):
        indices[s[x]] = x
    print indices
    vocabSize = len(indices)
    print "WN vocab size: %s" % len(indices)

    failed = set()
    # download image for concepts
    for w in concepts:
        ret = imgnet.download_image_urls(w, "/home/laga/uni/kurse/2013/ss/dist_semantik/hausarbeit/imgnet-data/")
        #time.sleep(0.3)
        if not ret:
            failed.add(w)

    print "Failed to download img for synsets: %s" % failed

    rep = {}
    for word in words:
        vector = [0 for x in xrange(0, 2 * vocabSize)]
        w1 = word["firstWordSynset"]
        w2 = word["secondWordSynset"]
        if w1 in failed or w2 in failed:
            print "Skipping current word, one of synsets does not have image: %s" % word
            continue
        rep[(w1,w2)] = vector
        for w in wn.get_hypernyms(w1, 7):
            idx = indices[w]
            vector[idx] = 1
        for w in wn.get_hypernyms(w2, 7):
            idx = indices[w]
            vector[idx] = 1
        vector.append(word["relation"])
    fh = open("wordnet.data", "w")
    for (key,val) in rep.iteritems():
        fh.write(key[0].name)
        fh.write(",")
        fh.write(key[1].name)
        fh.write(",")
        for f in val:
            fh.write(str(f))
            fh.write(",")
        fh.write("\n")
    fh.close()
    
    



if __name__ == "__main__":
    main()
        
