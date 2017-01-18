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
        // FOR FUTURE GRID SYSTEM
        if (app.config.DEBUG) utils.drawBoard();
        if (app.hud) app.hud.trigger('updateFPS', createjs.Ticker.getMeasuredFPS());

        // if (_.isEmpty(app.user) || app.commandsBlocked || app.keys[38] && app.keys[87] || app.keys[40] && app.keys[83] ||
        //   app.keys[39] && app.keys[68] || app.keys[37] && app.keys[65]) return;

        // if (app.keys[38] && app.keys[37] || app.keys[87] && app.keys[65]) {
        //     app.user.move(app.constants.Action.Walk, app.constants.Direction.NW);
        // }
        // else if (app.keys[38] && app.keys[39] || app.keys[87] && app.keys[68]) {
        //     app.user.move(app.constants.Action.Walk, app.constants.Direction.NE);
        // }
        // else if (app.keys[40] && app.keys[37] || app.keys[83] && app.keys[65]) {
        //     app.user.move(app.constants.Action.Walk, app.constants.Direction.SW);
        // }
        // else if (app.keys[40] && app.keys[39] || app.keys[83] && app.keys[68]) {
        //     app.user.move(app.constants.Action.Walk, app.constants.Direction.SE);
        // }

        // else if (app.keys[38] || app.keys[87]) {
        //     app.user.move(app.constants.Action.Walk, app.constants.Direction.N);
        // }
        // else if (app.keys[40] || app.keys[83]) {
        //     app.user.move(app.constants.Action.Walk, app.constants.Direction.S);
        // }
        // else if (app.keys[39] || app.keys[68]) {
        //     app.user.move(app.constants.Action.Walk, app.constants.Direction.E);
        // }
        // else if (app.keys[37] || app.keys[65]) {
        //     app.user.move(app.constants.Action.Walk, app.constants.Direction.W);
        // }

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
        if (app.keys[32]) {
            app.user.shoot();
        }
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

        // if (!_.isEmpty(app.user) && !app.keys[38] && !app.keys[87] && !app.keys[40] &&
        //     !app.keys[83] && !app.keys[39] && !app.keys[68] && !app.keys[37] &&
        //     !app.keys[65]) app.user.stop();
    });
    window.onbeforeunload = function() {
        var data = JSON.stringify({
            msg_type: 'unregister_user'
        })
        app.ws.send(data);
    };
});