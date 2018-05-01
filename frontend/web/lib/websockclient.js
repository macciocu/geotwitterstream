/**
 * @file WebsockClient.js
 * @author giovanni macciocu
 * @date Tue May  1 13:36:21 2018
 */

/**
 * constructor
 * @param host {string} host address (e.g. "localhost" or "127.0.0.1")
 * @param post {number} socket port (e.g. 8000)
 * @param logEn {bool} console logging enable / disable
 * @param fpRx {function} callback function which handles incoming data; fp(data)
 * @param fpOnOpen (function} callback function which handles websocket onopen event; fp()
 */
function WebsockClient(host, port, logEn, fpRx, fpOnOpen) {
    this.ws = null; // WebSocket
    this.host = host;
    this.port = port;
    this.logEn = logEn;
    this.fpRx = fpRx;
    this.fpOnOpen= fpOnOpen;
}

WebsockClient.prototype.connect = function() {
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

WebsockClient.prototype.disconnect = function() {
    this.ws.close();
};

WebsockClient.prototype.log = function(message) {
    if (this.logEn === true) {
        console.log(message);
    }
};

WebsockClient.prototype.onOpen = function(evt) {
    this.log("connected");
    this.tx('{"message":"Client says Hi!"}');
    this.fpOnOpen();
};

WebsockClient.prototype.onClose = function(evt) {
    this.log("disconnected");
};

WebsockClient.prototype.rx = function(evt) {
    this.log("Rx: " + evt.data);
    this.fpRx(evt.data);
};

WebsockClient.prototype.onError = function(evt) {
    this.ws.close()
    alert("Websocket client error: " + evt.data);
};

WebsockClient.prototype.tx = function(message) {
    this.log("Tx: " + message);
    this.ws.send(message);
};
