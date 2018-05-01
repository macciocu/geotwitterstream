#!/usr/bin/env python

'''
file: test.py
author: Giovanni Macciocu
date: Tue May  1 07:23:29 2018
'''

import logging
import os
import sys
import time

# relative directory package module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../backend/')
from geotwitterstream import GeoTwitterStreamService

# relative directory module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../backend/geotwitterstream')
from auth import GeoTwitterStreamAuth
from config import *
from server import *
from tweet import TweetCoord
from tweet import TweetMessage


def test_websocketserver():
    server = WebsocketServerImpl(CONFIG['SERVER_HOST'], CONFIG['SERVER_PORT'])


def test_geotwitterstreamauth():
    auth = GeoTwitterStreamAuth(CONFIG['CONSUMER_KEY'], CONFIG['CONSUMER_SECRET'],
            CONFIG['ACCESS_TOK'], CONFIG['ACCESS_TOK_SECRET'])

    geobox = TweetCoord()
    iter = auth.request_streaming_iterator(geobox)
    for tweetDict in iter:
        tweet = TweetMessage(tweetDict)
        print(tweet.userinfo())
        print(tweet.message())
        print(tweet.locationinfo())
        print(tweet.locationcoord())
        print('')


def test_geotwitterstreamservice():
    service = GeoTwitterStreamService()
    service.start()
    while True:
        time.sleep(10)


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    #logging.debug('test_websocketserver')
    #test_websocketserver()

    #logging.debug('test_geotwitterstreamauth')
    #test_geotwitterstreamauth()

    logging.debug('test_geotwitterstreamservice')
    test_geotwitterstreamservice()
