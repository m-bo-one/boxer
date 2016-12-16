var app = app || {};

$(function () {
    'use strict';

    var Socket = {
        ws: null,

        init: function () {
            ws = new WebSocket("ws://" + window.location.hostname + ":" + 9999 + "/game");

            ws.onmessage = function(evt) {
                var answer = JSON.parse(evt.data);
                var userData = answer.data;
                switch (answer.msg_type) {
                    case 'render_map':
                        canvas.width = userData.width;
                        canvas.height = userData.height;
                        break;
                    case 'register_user':
                        user = new app.UserModel(userData);
                        break;
                    case 'unregister_user':
                        users[userData.id].drop();
                        break;
                    case 'player_move':
                        user.update(userData);
                        break;
                    case 'users_map':
                        for (var user_id in userData) {
                            user_id = parseInt(user_id);
                            if (user.id !== user_id) {
                                if (users.hasOwnProperty(user_id)) {
                                    users[user_id].update(userData[user_id]);
                                } else {
                                    users[user_id] = new app.UserModel(userData[user_id]);   
                                }
                            }
                        }
                        break;
                }
            };
            ws.onopen = function(evt) {
                $('#conn_status').html('<b>WS Connected</b>');
            };
            ws.onerror = function(evt) {
                $('#conn_status').html('<b>WS Error</b>');
            };
            ws.onclose = function(evt) {
                $('#conn_status').html('<b>WS Closed</b>');
            };

            this.ws = ws;
        }
    };

    function gameLoop(event) {

        app.stage.update();
        console.log('Current FPS: ' + createjs.Ticker.getMeasuredFPS());

        if (app.user === null) return;

        if (app.keys[38] && app.keys[87] || app.keys[40] && app.keys[83] || app.keys[39] && app.keys[68] || app.keys[37] && app.keys[65]) return;

        if (app.keys[38] || app.keys[87]) {
            app.user.move('walk', 'top');
        }
        else if (app.keys[40] || app.keys[83]) {
            app.user.move('walk', 'bottom');
        }
        else if (app.keys[39] || app.keys[68]) {
            app.user.move('walk', 'right');
        }
        else if (app.keys[37] || app.keys[65]) {
            app.user.move('walk', 'left');
        }

        if (!app.keys[38] && !app.keys[87] && !app.keys[40] && !app.keys[83] && !app.keys[39] && !app.keys[68] && !app.keys[37] && !app.keys[65]) {
            app.user.stop();
        }
        
    }

    app.canvas = document.getElementById("myCanvas"),
    app.ctx = app.canvas.getContext("2d");
    app.keys = {};
    app.users = {};
    app.user = null;
    app.stage = new createjs.Stage(app.canvas);

    Socket.init();
    app.ws = Socket.ws;

    window.addEventListener("keydown", function (e) {
        keys[e.keyCode] = true;
    });
    window.addEventListener("keyup", function (e) {
        keys[e.keyCode] = false;
    });
    window.onbeforeunload = function() {
        var data = JSON.stringify({
            msg_type: 'unregister_user'
        })
        app.ws.send(data);
    };

    window.addEventListener("keydown", function (e) {
        app.keys[e.keyCode] = true;
    });
    window.addEventListener("keyup", function (e) {
        app.keys[e.keyCode] = false;
    });
});