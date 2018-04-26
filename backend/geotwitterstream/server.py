#!/usr/bin/env python

'''
Websocketserver documentation here: https://github.com/Pithikos/python-websocket-server
'''

import os
import logging
import socket

from contextlib import closing
from websocket_server import WebsocketServer


class WebsocketServerImpl(WebsocketServer):
    def __init__(self, host, port):
        WebsocketServer.__init__(self, host, port)
        logging.info('WebsocketServer created on %s:%s' % self.server_address)
