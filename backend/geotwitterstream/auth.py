'''
file: api.py
author: Giovanni Macciocu
date: Tue May  1 07:03:45 2018
'''

import json
import requests
import socket
import ssl
import time
import logging

from requests.exceptions import ConnectionError, ReadTimeout, SSLError
from requests.packages.urllib3.exceptions import ReadTimeoutError, ProtocolError
from requests_oauthlib import OAuth1


USER_AGENT = 'geotwitterstream v1.0'
RESOURCE_URL = 'https://stream.twitter.com/1.1/statuses/filter.json?locations='
# the twitter streaming API will send a keep-alive newline every 30 seconds
STREAM_TIMEOUT_SECONDS = 90


class GeoTwitterStreamAuth(object):
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        '''init with twitter application provided credentials for Oauth1 authorisation'''
        if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
            raise Exception('Missing necessary authentication argument for OAuth1 authentication.')
        self.auth = OAuth1(consumer_key, consumer_secret, access_token, access_token_secret)

    def request_streaming_iterator(self, geoboundingbox):
        '''request a streaming twitter API endpoint resource
        geoboundingbox -- {TweetCoord}
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



class _TwitterStreamIterable(object):
    def __init__(self, session_request_response):
        self.resp = session_request_response
        self.stream = session_request_response.raw

    def __del__(self):
        logging.debug('_TwitterStreamIterable destroyed (socket stream is closed)')

    def close(self):
        self.resp.close()

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

