define([''], function() {
    return {
        USE_SSL: false,
        FPS: 60,
        WS: {
            HOST: window.location.hostname,
            PORT: 9999
        },
        DEBUG: false,
        BOARD: {
            width: 1280,
            height: 768
        }
    };
});