define([
    'config',
    'backbone',
    'underscore',
    'easel'
], function(config, Backbone, _) {

    return {
        _LOG: function (msg) {
            if (config.DEBUG) console.log(msg);
        },
        toRadians(deg) {
            return deg * Math.PI / 180;
        },
        startTimer(duration, display) {
            var start = Date.now(),
                diff,
                minutes,
                seconds,
                _id;

            _id = setInterval(timer, 1000);
            function timer() {
                // get the number of seconds that have elapsed since 
                // startTimer() was called
                diff = duration - (((Date.now() - start) / 1000) | 0);

                // does the same job as parseInt truncates the float
                minutes = (diff / 60) | 0;
                seconds = (diff % 60) | 0;

                minutes = minutes < 10 ? "0" + minutes : minutes;
                seconds = seconds < 10 ? "0" + seconds : seconds;

                // display.textContent = minutes + ":" + seconds; 
                console.log(minutes + ":" + seconds);

                if (diff <= 0) {
                    // add one second so that the count down starts at the full duration
                    // example 05:00 not 04:59
                    // start = Date.now() + 1000;
                    clearInterval(_id);
                }
            };
            // we don't want to wait a full second before the timer starts
            timer();
        },
        underlinedText: function(options) {
            var cont = new createjs.Container();
            var text = new createjs.Text().set(options);
            text.textBaseline = "alphabetic";
            var w = text.getMeasuredWidth();

            var underline = new createjs.Shape();
            underline.graphics
                .s("black")
                .mt(text.x, text.y + 0.5)
                .lt(text.x + w, text.y + 0.5)
                .es();

            cont.addChild(text, underline);
            return cont;
        }
    };

});