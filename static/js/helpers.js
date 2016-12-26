var app = app || {};

var utils = (function() {

    'use strict';

    return {
        _LOG: function (msg) {
            if (app.config.DEBUG) {
                console.log(msg);
            }
        },
        toRadians(deg) {
            return deg * Math.PI / 180;
        },
        drawBoard() {
            app.ctx.beginPath();
            for (var x = 0; x <= app.canvas.width; x += app.canvas.width / 4) {
                app.ctx.moveTo(x, 0);
                app.ctx.lineTo(x, app.canvas.height);
            }

            for (var x = 0; x <= app.canvas.height; x += app.canvas.height / 4) {
                app.ctx.moveTo(0, x);
                app.ctx.lineTo(app.canvas.width, x);
            }

            app.ctx.strokeStyle = "black";
            app.ctx.stroke();
        }
    };
})();
