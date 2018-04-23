#!/usr/bin/env python

from requests.exceptions import ConnectionError, ReadTimeout, SSLError
from requests.packages.urllib3.exceptions import ReadTimeoutError, ProtocolError
from requests_oauthlib import OAuth1

import base64
import cStringIO
import httplib
import json
import urllib
import urllib2
import zlib
import os
from hashlib import sha1
import hmac
import requests
import socket
import ssl
import time
import logging

#https://developer.twitter.com/en/docs/basics/authentication/overview/application-only

'''
Access level	Read and write (modify app permissions)
Consumer Key (API Key)	77sZIhtpLTmykLRkIyOTebf7V (manage keys and access tokens)
Callback URL	None
Callback URL Locked	No
Sign in with Twitter	Yes
App-only authentication	https://api.twitter.com/oauth2/token
Request token URL	https://api.twitter.com/oauth/request_token
Authorize URL	https://api.twitter.com/oauth/authorize
Access token URL	https://api.twitter.com/oauth/access_token
'''

RESOURCE_URL = 'https://stream.twitter.com/1.1/statuses/filter.json'

CONSUMER_KEY = '77sZIhtpLTmykLRkIyOTebf7V'
# TODO Keep the "Consumer Secret" a secret. This key should never be human-readable in your application.
CONSUMER_SECRET = 'UP7CvZHinRCj4IyYfC6vmrH187pPIQQ5CD3CJIwde4f5wydWR1'
# TODO This access token can be used to make API requests on your own account's behalf. Do not
# share your access token secret with anyone.
ACCESS_TOK = '570855470-qwZHnkeeLL9D0JHPUgkfx8czIxBpRNVB6COFGrgW'
ACCESS_TOK_SECRET = 'Px3qOO1js9icEmwqcGGc0q1izDCUMg88PrSD5vuv6sPLL'

USER_AGENT = 'geotwitterstream v1.0'
STREAM_TIMEOUT_SECONDS = 100

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
APP_ONLY_AUTH_URL = 'https://api.twitter.com/oauth2/token'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'

class GeoBoundingBox(object):
    def __init__(self, latitude_longitude_a=(40, -74), latitude_longitude_b=(41, -73)):
        '''
        latitude_longitude_a --- (latitude, longitude) pair A of bounding box
        latitude_longitude_b --- (latitude, longitude) pair B of bounding box
        '''
        self._latitude_longitude_a = latitude_longitude_a
        self._latitude_longitude_b = latitude_longitude_b

    @property
    def latitude_longitude_a(self):
        return self._latitude_longitude_a

    @property
    def latitude_longitude_b(self):
        return self._latitude_longitude_b

    @latitude_longitude_a.setter
    def latitude_longitude_a(self, val):
        self._latitude_longitude_a = val

    @latitude_longitude_b.setter
    def latitude_longitude_b(self, val):
        self._latitude_longitude_b = val

    def __str__(self):
        return '%s,%s,%s,%s' % (self._latitude_longitude_a[1], self._latitude_longitude_a[0],
                self._latitude_longitude_b[1], self._latitude_longitude_b[0])


class _TwitterStreamIterable(object):
    def __init__(self, session_request_response):
        self.stream = session_request_response.raw

    def _parse_stream_iter(self):
        while True:
            item = None
            buf = bytearray()
            stall_timer = None
            try:
                while True:
                    # read bytes until item boundary reached
                    buf += self.stream.read(1)
                    if not buf:
                        # check for stall (i.e. no data for STREAM_TIMEOUT_SECONDS)
                        if not stall_timer:
                            stall_timer = time.time()
                        elif time.time() - stall_timer > STREAM_TIMEOUT_SECONDS:
                            raise Exception('Twitter stream stalled')
                    elif stall_timer:
                        stall_timer = None
                    if buf[-2:] == b'\r\n':
                        item = buf[0:-2]
                        if item.isdigit():
                            # use byte size to read next item
                            nbytes = int(item)
                            item = None
                            item = self.stream.read(nbytes)
                        break
                yield item
            except (ConnectionError, ProtocolError, ReadTimeout, ReadTimeoutError,
                    SSLError, ssl.SSLError, socket.error) as e:
                raise Exception('%s %s' % (type(e), e))
            except AttributeError:
                # inform iterator to exit when client closes connection
                raise Exception('stream iteration attribute error')

    def __iter__(self):
        '''Iterator.
        returns: Tweet status as a JSON object.
        '''
        for item in self._parse_stream_iter():
            if item:
                try:
                    yield json.loads(item.decode('utf8'))
                except ValueError as e:
                    # invalid JSON string (possibly an unformatted error message)
                    raise Exception('Invalid JSON string %s %s' % (type(e), e))


class Tweet(object):
    def __init__(self, tweet):
        self._tweet = tweet

    def __str__(self):
        for key in self._tweet:
            print('%s: %s' % (key, self._tweet[key]))

    def print_userinfo(self):
        if 'user' not in self._tweet:
            print('user: not available')
        else:
            info = ''
            if 'name' in self._tweet['user']:
                info += '%s' % (self._tweet['user']['name'])
            if 'id' in self._tweet['user']:
                info += ' (%s)' % (self._tweet['user']['description'])
            if 'description' in self._tweet['user']:
                info += ' - %s' % (self._tweet['user']['description'])
            print(info)

    def print_message(self):
        if 'text' not in self._tweet:
            print('text: not available')
        else:
            print(self._tweet['text'])

    def print_locationinfo(self):
        if 'place' not in self._tweet:
            print('geo: not available')
        else:
            info = ''
            if 'country' in self._tweet['place']:
               info = self._tweet['place']['country']
            if 'country_code' in self._tweet['place']:
                info += ' (%s)' % (self._tweet['place']['country_code'])
            if 'full_name' in self._tweet['place']:
                info += ' - %s' % (self._tweet['place']['full_name'])
            if info != '':
                print(info)

    def print_locationcoord(self):
        if 'bounding_box' in self._tweet['place']:
            if 'coordinates' in self._tweet['place']['bounding_box']:
                # 3d list [[[longitude, latitude], [longitude, latitude] ...]]
                bounding_box_coord = self._tweet['place']['bounding_box']['coordinates']
                for location in bounding_box_coord:
                    print location
                    for longitude_latitude in location:
                        print('  (latitude | longitude) - (%s | %s)' % (longitude_latitude[1],
                                longitude_latitude[0]))


class TwitterStreamAPIAuth(object):
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        '''
        consumer_key -- twitter provided key for geotwitterstream application
        consumer_secret -- twitter provided secret for geotwitterstream application
        access_token -- twitter provided access token
        access_token_secret -- twitter provided access token secret
        '''
        if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
            raise Exception('Missing necessary authentication argument for OAuth1 authentication.')
        self.auth = OAuth1(consumer_key, consumer_secret, access_token, access_token_secret)

    def request_streaming_iterator(self, url):
        '''request a streaming twitter API endpoint resource'''

        with requests.Session() as session:
            session.auth = self.auth
            session.headers = {'User-Agent': USER_AGENT}
            session.stream = True

            try:
                response = session.request('GET', url, data=None, params=None,
                        timeout=STREAM_TIMEOUT_SECONDS, files=None, proxies=None)
            except (ConnectionError, ProtocolError, ReadTimeout, ReadTimeoutError, SSLError,
                    ssl.SSLError, socket.error) as e:
                raise Exception('%s %s' % (type(e), e))

            if response.status_code != 200:
                raise Exception('session.request response.status_code = %s' % response.status_code)

            print(response.headers)
            print(response.status_code)

            return iter(_TwitterStreamIterable(response))

    @staticmethod
    def test():
        auth = TwitterStreamAPIAuth(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOK, ACCESS_TOK_SECRET)

        geobox = GeoBoundingBox()
        url = RESOURCE_URL+'?locations='+str(geobox)
        print(url)

        iter = auth.request_streaming_iterator(url)
        for tweetDict in iter:
            tweet = Tweet(tweetDict)
            tweet.print_userinfo()
            tweet.print_message()
            tweet.print_locationinfo()
            tweet.print_locationcoord()
            print('')

if __name__ == "__main__":
    TwitterStreamAPIAuth.test()
