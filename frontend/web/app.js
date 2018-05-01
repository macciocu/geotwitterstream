let CONFIG = {
    RELEASE: false,
    SERVER_HOST: 'localhost',
    SERVER_PORT: 2000,
    //TWEETDATA_MAXCHARS: 10000000
    TWEETDATA_MAXCHARS: 10000
};

// WebsockClient
let wsc = null;
// latitude, longitude pair A
let latA = null;
let longA = null;
// latitude, longitude pair B
let latB = null;
let longB = null;

function onclickSetLocation() {
    let latA = document.getElementById('id-latitude_a').value;
    let longA = document.getElementById('id-longitude_a').value;
    let latB = document.getElementById('id-latitude_b').value;
    let longB = document.getElementById('id-longitude_b').value;

    let tail =
        '?lat-a='+latA+
        '&long-a='+longA+
        '&lat-b='+latB+
        '&long-b='+longB;

    let urlSplit = window.location.href.split('?');
    if (urlSplit.length > 1) {
        window.location.href = urlSplit[0] + tail;
    } else {
        window.location.href = window.location.href + tail;
    }
}

function fpWebsocketRxCallb(data) {
    let prevData = document.getElementById('id-tweets').innerHTML;
    if (prevData.length > CONFIG.TWEETDATA_MAXCHARS) {
        prevData = prevData.substring(0, CONFIG.TWEETDATA_MAXCHARS - data.length);
    }
    document.getElementById('id-tweets').innerHTML = data + '<br/>' + prevData;
}

function fpWebsocketOnOpenCallb() {
    console.log('fpWebsocketOnOpenCallb');
    wsc.tx(
        '{"command":"set_geo",'+
         '"latitude_a":'+latA+','+
         '"longitude_a":'+longA+','+
         '"latitude_b":'+latB+','+
         '"longitude_b":'+longB+
        '}');
}

window.onload = function() {
    let urlSplit = window.location.href.split('?');
    if (urlSplit.length > 1) {
        paramSplit = urlSplit[1].split('&');
        latA = paramSplit[0].split('=')[1];
        longA = paramSplit[1].split('=')[1];
        latB = paramSplit[2].split('=')[1];
        longB = paramSplit[3].split('=')[1];

        document.getElementById('id-latitude_a').value = latA;
        document.getElementById('id-longitude_a').value = longA;
        document.getElementById('id-latitude_b').value = latB;
        document.getElementById('id-longitude_b').value = longB;

        wsc = new WebsockClient(CONFIG.SERVER_HOST, CONFIG.SERVER_PORT, !CONFIG.RELEASE,
                fpWebsocketRxCallb, fpWebsocketOnOpenCallb);
        wsc.connect();
    }
};
