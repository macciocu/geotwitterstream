#!/usr/bin/env python

# requirements:
#   pip install requests
#   pip install requests_oauthlib

from requests.exceptions import ConnectionError, ReadTimeout, SSLError
from requests.packages.urllib3.exceptions import ReadTimeoutError, ProtocolError
from requests_oauthlib import OAuth1

from .server import WebsocketServerImpl
from .config import *

from enum import Enum

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
import datetime

USER_AGENT = 'geotwitterstream v1.0'
RESOURCE_URL = 'https://stream.twitter.com/1.1/statuses/filter.json?locations='
STREAM_TIMEOUT_SECONDS = 100


class GeoTwitterStreamServiceStatusCode(Enum):
    IDLE = 0
    RUNNING = 1
    ERROR = 2


class GeoTwitterStreamServiceStatus(object):
    def __init__(self, status_code, status_message):
        self.status_code = status_code;
        self.status_message = status_message


class GeoTwitterStreamService(object):
    def __init__(self):
        self._auth = GeoTwitterStreamAuth(CONFIG['CONSUMER_KEY'], CONFIG['CONSUMER_SECRET'],
                CONFIG['ACCESS_TOK'], CONFIG['ACCESS_TOK_SECRET'])

        self._wss = WebsocketServerImpl(CONFIG['SERVER_HOST'], CONFIG['SERVER_PORT'])
        self._wss.register_rxhandle('set_geo', self.set_geo)

    def set_geo(self, data):
        print('set_get '+str(data)) # TODO

    def status(self):
        return (self._status_code, self.status_message)

    def start(self, geoTwitterStreamBoundingBox):
        self._status_code = GeoTwitterStreamServiceStatusCode.RUNNING
        self._status_message = 'Started at: %s' % (datetime.datetime.now())
        # TODO send stream to server in separate thread, or something like that
        return self._auth.request_streaming_iterator(geoTwitterStreamBoundingBox)

    def stop(self):
        self._status_code = GeoTwitterStreamServiceStatusCode.IDLE
        self._status_message = 'Stopped at: %s' % (datetime.datetime.now)


class GeoTwitterStreamAuth(object):
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        '''init with twitter application provided credentials for Oauth1 authorisation'''
        if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
            raise Exception('Missing necessary authentication argument for OAuth1 authentication.')
        self.auth = OAuth1(consumer_key, consumer_secret, access_token, access_token_secret)

    def request_streaming_iterator(self, geoboundingbox):
        '''request a streaming twitter API endpoint resource
        geoboundingbox -- {GeoTwitterStreamBoundingBox}
        '''
        with requests.Session() as session:
            session.auth = self.auth
            session.headers = {'User-Agent': USER_AGENT}
            session.stream = True
            url = RESOURCE_URL + str(geoboundingbox)

            try:
                response = session.request('GET', url, data=None, params=None,
                        timeout=STREAM_TIMEOUT_SECONDS, files=None, proxies=None)
            except (ConnectionError, ProtocolError, ReadTimeout, ReadTimeoutError, SSLError,
                    ssl.SSLError, socket.error) as e:
                raise Exception('%s %s' % (type(e), e))

            if response.status_code != 200:
                raise Exception('session.request response.status_code = %s' % response.status_code)

            return iter(_TwitterStreamIterable(response))


class GeoTwitterStreamBoundingBox(object):
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
        for item in self._parse_stream_iter():
            if item:
                try:
                    yield json.loads(item.decode('utf8'))
                except ValueError as e:
                    # invalid JSON string (possibly an unformatted error message)
                    raise Exception('Invalid JSON string %s %s' % (type(e), e))


class GeoTwitterStreamTweet(object):
    def __init__(self, tweet):
        self._tweet = tweet

    def __str__(self):
        for key in self._tweet:
            print('%s: %s' % (key, self._tweet[key]))

    def print_userinfo(self):
        if 'user' not in self._tweet:
            print('user-info: not available')
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
            print('message-text: not available')
        else:
            print(self._tweet['text'])

    def print_locationinfo(self):
        if 'place' not in self._tweet:
            print('location-info: not available')
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
        coordinates_available = False
        if 'bounding_box' in self._tweet['place']:
            if 'coordinates' in self._tweet['place']['bounding_box']:
                coordinates_available = True
                # 3d list [[[longitude, latitude], [longitude, latitude] ...]]
                bounding_box_coord = self._tweet['place']['bounding_box']['coordinates']
                for location in bounding_box_coord:
                    for longitude_latitude in location:
                        print('  (latitude | longitude) - (%s | %s)' % (longitude_latitude[1],
                                longitude_latitude[0]))
        if not coordinates_available:
            print('geo-coordinates: not available')
