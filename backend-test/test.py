#!/usr/bin/env python

import logging
import os
import sys

# relative directory package module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../backend/')
from geotwitterstream import GeoTwitterStreamAuth
from geotwitterstream import GeoTwitterStreamBoundingBox
from geotwitterstream import GeoTwitterStreamTweet
from geotwitterstream import GeoTwitterStreamService

# relative directory module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../backend/geotwitterstream')
from server import *
from config import *


def test_websocketserver():
    server = WebsocketServerImpl(CONFIG['SERVER_HOST'], CONFIG['SERVER_PORT'])


def test_geotwitterstreamauth():
    auth = GeoTwitterStreamAuth(CONFIG['CONSUMER_KEY'], CONFIG['CONSUMER_SECRET'],
            CONFIG['ACCESS_TOK'], CONFIG['ACCESS_TOK_SECRET'], CONFIG['SERVER_CONNECT_PATH'])

    geobox = GeoTwitterStreamBoundingBox()
    iter = auth.request_streaming_iterator(geobox)
    for tweetDict in iter:
        tweet = GeoTwitterStreamTweet(tweetDict)
        tweet.print_userinfo()
        tweet.print_message()
        tweet.print_locationinfo()
        tweet.print_locationcoord()
        print('')


def test_geotwitterstreamservice():
    service = GeoTwitterStreamService()
    service.start()


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    #logging.debug('test_websocketserver')
    #test_websocketserver()

    #logging.debug('test_geotwitterstreamauth')
    #test_geotwitterstreamauth()

    logging.debug('test_geotwitterstreamservice')
    test_geotwitterstreamservice()
