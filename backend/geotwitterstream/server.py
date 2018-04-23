#!/usr/bin/env python

'''
Websocketserver documentation here: https://github.com/Pithikos/python-websocket-server
'''

import logging
import socket

from contextlib import closing
from websocket_server import WebsocketServer


class WebsocketServerImpl(WebsocketServer):
    def __init__(self, host='localhost', port=None):
        WebsocketServer.__init__(self, port, host)
        logging.info('WebsocketServer created on %s:%s' % self.server_address)


class WebsocketServerFactory(object):
    def __init__(self):
        pass

    def create(self, host='localhost', port=None):
        '''Create WebsocketServer instance for the first detected available port.'''
        if port is None:
            port = self._detect_available_port()
        return WebsocketServerImpl(host, port)

    def _detect_available_port(self):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.bind(('', 0))
            return sock.getsockname()[1]


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    wssfactory = WebsocketServerFactory()
    wss = wssfactory.create()
