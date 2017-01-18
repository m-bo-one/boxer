var app = app || {},
    utils = utils || {};

$(function () {
    'use strict';

    var gameLoop = function (event) {
        /** Keys notation
        * 49 - '1'
        * 38 - 'w'
        * 40 - 's'
        * 39 - 'd'
        * 37 - 'a'
        * 87 - key up
        * 83 - key down
        * 68 - key right
        * 65 - key left
        **/

        app.stage.update();
        if (app.user.currentSprite && app.user.currentSprite.cacheCanvas) app.user.currentSprite.updateCache();
        if (app.config.DEBUG) utils.drawBoard();
        if (app.hud) app.hud.trigger('updateFPS', createjs.Ticker.getMeasuredFPS());

    };

    app.canvas = document.getElementById("gameBoard");
    app.canvas.width = 1280;
    app.canvas.height = 768;
    app.canvas.style.backgroundColor = "black";
    app.ctx = app.canvas.getContext("2d");
    app.keys = {};
    app.users = {};
    app.user = {};
    app.sprites = {};
    app.stage = new createjs.Stage(app.canvas);
    app.stage.enableMouseOver(10);
    // createjs.Ticker.timingMode = createjs.Ticker.RAF_SYNCHED;
    createjs.Ticker.setFPS(app.config.GAME.FPS);
    createjs.Ticker.addEventListener("tick", gameLoop);

    window.addEventListener("keydown", function (e) {
        app.keys[e.keyCode] = true;
        // button '1'
        if (app.keys[49]) {
            app.user.equipWeapon();
        }
        // button 'space'
        // if (app.keys[32]) {
        //     app.user.shoot();
        // }
        // button 'H'
        if (app.keys[72]) {
            app.user.heal();
        }

        // 0   48
        // 1   49
        // 2   50
        // 3   51

        // button '3'
        if (app.keys[51]) {
            app.user.stealth();
        }        
    });
    window.addEventListener("keyup", function (e) {
        app.keys[e.keyCode] = false;
    });
    window.onbeforeunload = function() {
        var data = JSON.stringify({
            msg_type: 'unregister_user'
        })
        app.ws.send(data);
    };
});