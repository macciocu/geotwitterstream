#!/usr/bin/env python

import logging
import os
import sys

# file directory package imports
from credentials import *

# relative directory package module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../backend/')
from geotwitterstream import GeoTwitterStreamAuth
from geotwitterstream import GeoTwitterStreamBoundingBox
from geotwitterstream import GeoTwitterStreamTweet

# relative directory module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../backend/geotwitterstream')
from server import WebsocketServerFactory


def test_websocketserver():
    wssfactory = WebsocketServerFactory()
    wss = wssfactory.create()


def test_geotwitterstreamauth():
    auth = GeoTwitterStreamAuth(CREDENTIALS['CONSUMER_KEY'], CREDENTIALS['CONSUMER_SECRET'],
            CREDENTIALS['ACCESS_TOK'], CREDENTIALS['ACCESS_TOK_SECRET'])

    geobox = GeoTwitterStreamBoundingBox()
    iter = auth.request_streaming_iterator(geobox)
    for tweetDict in iter:
        tweet = GeoTwitterStreamTweet(tweetDict)
        tweet.print_userinfo()
        tweet.print_message()
        tweet.print_locationinfo()
        tweet.print_locationcoord()
        print('')


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    logging.debug('test_websocketserver')
    test_websocketserver()

    logging.debug('test_geotwitterstreamauth')
    test_geotwitterstreamauth()
