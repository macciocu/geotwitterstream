function rx(data) {

}

window.onload = function() {
    let RELEASE = false;

    //coordWin = new CoordWin('win-coord');
    //twitterStreamWin = new TwitterStreamWin('win-twitterStream');


    //coordWin.doc();
    //twitterStream.doc();

    let wsc = new WebsockClient(host, port, rx, RELEASE);
    wsc.connect();
    wsc.tx('Hi from frontend');
}
