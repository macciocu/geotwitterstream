'''
file: service.py
author: Giovanni Macciocu
date: Tue May  1 08:36:56 2018
'''

import datetime
import threading
from enum import Enum

from .auth import *
from .config import *
from .server import *
from .tweet import *


class GeoTwitterStreamServiceStatusCode(Enum):
    IDLE = 0
    RUNNING = 1
    ERROR = 2


class GeoTwitterStreamService(object):
    _txworker_run = {}
    _txworker_threads = {}

    def __init__(self):
        self._status_code = GeoTwitterStreamServiceStatusCode.IDLE
        self._status_message = 'Idle since: %s' % (datetime.datetime.now())

        self._auth = GeoTwitterStreamAuth(CONFIG['CONSUMER_KEY'], CONFIG['CONSUMER_SECRET'],
                CONFIG['ACCESS_TOK'], CONFIG['ACCESS_TOK_SECRET'])

        self._wss = WebsocketServerImpl(CONFIG['SERVER_HOST'], CONFIG['SERVER_PORT'])
        self._wss.register_rxhandle('set_geo', self.set_geo)

    @staticmethod
    def _txworker(wss, client, twitter_stream_iter):
        '''worker thread for sending twitter stream to connected websocket server client
        wss -- {WebsocketServerImpl}
        client -- wss connected client to which stream will be sent
        twitter_stream_iter -- {_TwitterStreamIterable}
        '''
        for tweetDict in twitter_stream_iter:
            if not GeoTwitterStreamService._txworker_run[client['id']]:
                twitter_stream_iter.close()
            else:
                tweet = TweetMessage(tweetDict);
                mssg = ('<p><h3>'+tweet.userinfo()+'</h3>'+tweet.message()+'<br/>'+
                        tweet.locationinfo()+'<br/>'+tweet.locationcoord()+'</p>')
                #print(tweet.message)
                try:
                    wss.send_message(client, mssg)
                except:
                    logging.info('client connection lost')
                    break

    def set_geo(self, client, dict):
        if client['id'] in self._txworker_run:
            GeoTwitterStreamService._txworker_run[client['id']] = False
            GeoTwitterStreamService._txworker_threads[client['id']].join()

        latitude_longitude_a = (dict['latitude_a'], dict['longitude_a'])
        latitude_longitude_b = (dict['latitude_b'], dict['longitude_b'])
        geobox = TweetCoord(latitude_longitude_a, latitude_longitude_b)
        iter = self._auth.request_streaming_iterator(geobox)
        thread = threading.Thread(target=GeoTwitterStreamService._txworker,
                args=(self._wss, client, iter))

        GeoTwitterStreamService._txworker_run[client['id']] = True
        GeoTwitterStreamService._txworker_threads[client['id']] = thread
        thread.start()

    def status(self):
        return (self._status_code, self._status_message)

    def start(self):
        self._status_code = GeoTwitterStreamServiceStatusCode.RUNNING
        self._status_message = 'Started at: %s' % (datetime.datetime.now())
        self._wss.run_forever()

    def stop(self):
        self._status_code = GeoTwitterStreamServiceStatusCode.IDLE
        self._status_message = 'Stopped at: %s' % (datetime.datetime.now)
