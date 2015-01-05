#!/usr/bin/env python

#import time
#import sys
#import os
#import signal
#import logging
#import json
import urllib.request
from xml.dom import minidom

repositoryUrl = "http://instead-launcher.googlecode.com/svn/pool/game_list.xml"
response = urllib.request.urlopen(repositoryUrl)
f = response
xmldoc = minidom.parse(f)
gameList = xmldoc.getElementsByTagName('game')

for game in gameList :
    title = game.getElementsByTagName("title")[0]
    version = game.getElementsByTagName("version")[0]
    print("%s %s" % (title.firstChild.data, version.firstChild.data))
