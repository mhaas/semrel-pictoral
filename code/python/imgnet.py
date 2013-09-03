#!/usr/bin/python2
# -*- coding: utf-8 -*-

from nltk.corpus import wordnet as wn
import urllib2
import random
import time
import os
import socket
import httplib

LBASE = "http://www.image-net.org/api/text/imagenet.synset.geturls?wnid="

def mark(fileName):
    fh = open(fileName, "w")
    fh.write("failed\n")
    fh.close()


def get_urls(synset):
    offset = str(synset.offset).rjust(8, "0")
    pos = synset.pos
    url = LBASE + pos + offset
    fh = urllib2.urlopen(url)
    image_urls = fh.readlines()
    if "Invalid url!" in image_urls or "The synset is not ready yet. Please stay tuned!" in image_urls:
        print "got 'invalid url'"
        return None
    return image_urls

def download_image(image_urls, out, offset, orig ):
    # now try to download an image
    x = 0
    while x < 5:
        try:
            x = x+1
            u = random.choice(image_urls)
            if u is None:
                continue
            image_urls.remove(u)
            print "Chosen random image: %s" % u
            ifh = urllib2.urlopen(u)
            img = ifh.read()
            outfh = open(out + "." + str(offset) + ".img", "w")
            outfh.write(img)
            outfh.close()
            outfh = open(out + "." + str(offset) + ".img.url", "w")
            outfh.write(u)
            outfh.write("\n")
            outfh.close()
            outfh = open(out + "." + str(offset) + ".img.synsetid", "w")
            outfh.write(orig.name)
            outfh.write("\n")
            outfh.close()

        except urllib2.HTTPError:
            print "got httperror, retry"
        except urllib2.URLError:
            print "got urlError, retry"
        except ValueError:
            print "got valueerror, retry"
        except socket.error:
            print "got socket error, retry"
        except httplib.BadStatusLine:
            print "got httplib.BadStatusLine. retry"
        return True
    mark(failOut)
    return False


def download_image_urls(synset, dest):


    failOut = dest + "/" + synset.name + ".failed"
    winOut = dest + "/" + synset.name + ".img.0.img"
    if (os.path.exists(winOut)):
        print "skip"
        return True
    if (os.path.exists(failOut)):
        print "failskip"
        return False

    hypernym = synset
    image_urls = get_urls(hypernym)
    try:
        if image_urls is None:
            print "Synset unknown or not ready, going to hypernym"
            hypernym = random.choice(synset.hypernyms())
            image_urls = get_urls(hypernym)
        if image_urls is None:
            print "Synset unknown or not ready, going to hypernym"
            hypernym = random.choice(hypernym.hypernyms())
            image_urls = get_urls(hypernym)
    except IndexError:
        pass
    if image_urls is None:
        print "got 'invalid url'"
        mark(failOut)
        return False
    
    
    # now try to download an image
    ret = download_image(image_urls, winOut, 0, hypernym)
    workedOnce = ret
    count = 0
    while ret and len(image_urls) > 0 and count < 5:
        ret = download_image(image_urls, winOut, count + 1, hypernym)
        count += 1
    return workedOnce
        

