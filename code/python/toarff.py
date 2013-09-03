#!/usr/bin/python2
# -*- coding: utf-8 -*-
import os
import glob
import re
import wn

def wn_to_arff(fileName, out, imgPath):

    writeIMG = True

    classes = [ "quality", "participant", "temporal", "spatial", "causal" ]

    fh = open(fileName, "r")
    lines = fh.readlines()
    fh.close()

    for clazz in classes:
        count = 0
        outName = out + ".WN." + clazz + ".arff"
        if writeIMG:
            outName = out + ".IMG." + clazz + ".arff"
        outfh = open(outName, "w")
        outfh.write("@relation wordnetdata\n")
        outfh.write("@attribute firstWord String\n")
        outfh.write("@attribute secondWord String\n")
        for i in xrange(0, 2  * 897):
            outfh.write("@attribute dim%s Numeric\n" % i)
        if writeIMG:
            for i in xrange(0, 2*1000):
                outfh.write("@attribute img%s Numeric\n" % i)
        outfh.write("@attribute class {" + clazz + ", not-" + clazz  + "}\n")
        outfh.write("@data\n")


        imgCache = load_imgs(imgPath)
        
        cc = set(imgCache.keys())
        
        for line in lines:
            line = line.strip()[:-1]
            items = line.split(",")
            items[0] = "'" + items[0] + "'"
            items[1] = "'" + items[1] + "'"
            syn1 = wn.get_synset_from_id(items[0])
            syn2 = wn.get_synset_from_id(items[1])
            i1 = None
            i2 = None
            if syn1 in imgCache:
                i1 = get_img(imgCache[syn1])
            cc.discard(syn1)
            if syn2 in imgCache:
                i2 = get_img(imgCache[syn2])
            cc.discard(syn2)
            if i1 is None:
                print "Not found: img for %s" % items[0]
                continue
            if i2 is None:
                print "Not found: img for %s" % items[1]
                continue
            #print "len i1 %s, i2 %s" % (len(i1), len(i2))
            count += 1
            instanceClass = items[-1]
            del items[-1]
            if instanceClass != clazz:
                instanceClass = "not-" + clazz
            outfh.write(",".join(items))
            if writeIMG:
                outfh.write(",")
                outfh.write(",".join(i1))
                outfh.write(",")
                outfh.write(",".join(i2))
            outfh.write(",")
            outfh.write(instanceClass)
            outfh.write("\n")
        outfh.close()
        print "got %s items" % count
        print "Never touched these imgs: %s" % cc

def load_imgs(path):
    res = {}
    regex = re.compile(ur"^(.*\.n\..{1,2})")
    for fileName in glob.glob(path + "/*.img.0.img.bownormalized.simple"):
        n = fileName.split("/")[-1]
        match = regex.match(n)
        sid = match.group(1)
        synset = wn.get_synset_from_id(sid)
        res[synset] = fileName
    return res
        
def get_img(path):
    #print "looking up path %s" % p
    fh = open(path, "r")
    l = fh.readline()
    items = l[1:-1].split(",")
    return items
    
    

if __name__ == "__main__":
    import sys
    wn_to_arff(sys.argv[1], sys.argv[2], sys.argv[3])
    #load_imgs(sys.argv[1])
