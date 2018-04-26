function rx(data) {

}

window.onload = function() {
    let RELEASE = false;
    let wsc = new WebsockClient(host, port, rx, RELEASE);
    wsc.connect();
    wsc.tx('Hi from frontend');
}
