'''
Websocketserver documentation here: https://github.com/Pithikos/python-websocket-server
'''

import json
import os
import logging
import socket

from contextlib import closing
from websocket_server import WebsocketServer


class WebsocketServerImpl(WebsocketServer):
    _commands = [] # registered command string
    _fps = [] # registered function pointer for corresponding command entry

    def __init__(self, host, port):
        WebsocketServer.__init__(self, port, host)
        logging.info('WebsocketServer created on %s:%s' % self.server_address)

        # register callbacks
        self.set_fn_new_client(WebsocketServerImpl._client_connect)
        self.set_fn_client_left(WebsocketServerImpl._client_disconnect)
        self.set_fn_message_received(WebsocketServerImpl._rx)

    def register_rxhandle(self, command, fp):
        WebsocketServerImpl._commands.append(command)
        WebsocketServerImpl._fps.append(fp)

    @staticmethod
    def _client_connect(client, server):
        logging.info('client %s has connected to server %s' % (client, server))

    @staticmethod
    def _client_disconnect(client, server):
        logging.info('client %s is disconnected from server %s' % (client, server))

    @staticmethod
    def _rx(client, server, rxdata):
        print(str(rxdata));
        dict = json.loads(rxdata.decode('utf8'))
        if 'message' in dict:
            logging.info(dict['message'])
        elif 'command' in dict:
            rxcmd = dict['command']
            for idx, cmd in enumerate(WebsocketServerImpl._commands):
                if rxcmd == cmd:
                    WebsocketServerImpl._fps[idx](client, dict)
                    break
