#!/usr/bin/env python

import os
import sys

# file directory package imports
from credentials import *

# relative directory package imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../backend/')
from geotwitterstream import GeoTwitterStreamAuth
from geotwitterstream import GeoTwitterStreamBoundingBox
from geotwitterstream import GeoTwitterStreamTweet


if __name__ == "__main__":
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
