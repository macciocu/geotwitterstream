/**
 * @file websockclient.js
 * @author giovanni macciocu
 * @date 29 May 2016
 */

/**
 * constructor
 * @param host (string) host address (e.g. "localhost" or "127.0.0.1")
 * @param post (number) socket port (e.g. 8000)
 * @param logEn (true / false) console logging enable / disable
 */
function Websockclient(host, port, logEn) {
    this.ws = null;
    this.host = host;
    this.port = port;
    this.logEn = logEn;
}

Websockclient.prototype.connect = function() {
    if (!("WebSocket" in window)) {
        alert("WebSocket is NOT supported!");
    } else {
        uri = "ws://" + this.host + ":" + this.port;
        this.ws = new WebSocket(uri);
        this.ws.onopen = this.onOpen.bind(this);
        this.ws.onclose = this.onClose.bind(this);
        this.ws.onmessage = this.rx.bind(this);
        this.ws.onerror = this.onError.bind(this);
    }
};

Websockclient.prototype.disconnect = function() {
    this.ws.close();
};

Websockclient.prototype.log = function(message) {
    if (this.logEn == true) {
        trace.info(message);
    }
};

Websockclient.prototype.onOpen = function(evt) {
    this.log("connected");
    this.tx("Client says Hi!");
};

Websockclient.prototype.onClose = function(evt) {
    this.log("disconnected");
};

Websockclient.prototype.rx = function(evt) {
    this.log("Rx: " + evt.data);
};

Websockclient.prototype.onError = function(evt) {
    this.ws.close()
    alert("Websocket client error: " + evt.data);
};

Websockclient.prototype.tx = function(message) {
    this.log("Tx: " + message);
    this.ws.send(message);
};

