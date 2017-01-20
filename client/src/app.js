define(['config', 'jquery', 'backbone', 'easel'], function(config, $, Backbone) {

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
        // if (app.user.currentSprite && app.user.currentSprite.cacheCanvas) {
        //     app.user.currentSprite.updateCache();
        // }
        // if (app.config.DEBUG) utils.drawBoard();
        if (app.currentCharacter) {
            app.currentCharacter.hud.trigger('updateFPS', createjs.Ticker.getMeasuredFPS());
        }

    };

    window.app = {};
    app.config = config;
    app.canvas = document.getElementById("gameBoard");
    app.canvas.width = 1280;
    app.canvas.height = 768;
    app.canvas.style.backgroundColor = "white";
    app.ctx = app.canvas.getContext("2d");
    app.keys = {};
    app.characters = {};
    app.shootMode = false;
    app.currentCharacter = null;
    app.stage = new createjs.Stage(app.canvas);
    app.stage.enableMouseOver(10);

    createjs.Ticker.addEventListener("tick", gameLoop);
    createjs.Ticker.setFPS(app.config.FPS);

    window.addEventListener("keydown", function (e) {
        app.keys[e.keyCode] = true;
        switch (e.keyCode) {
            // button 'Z'
            case 90:
                app.currentCharacter.model.equipWeapon();
                break;
            // button 'H'
            case 72:
                app.currentCharacter.model.heal();
                break;
            // button 'Q'
            case 81:
                app.currentCharacter.model.stealth();
                break;
            // button 'W'
            case 87:
                // TODO
                break;
            // button 'E'
            case 69:
                // TODO
                break;
            // button 'R'
            case 82:
                // TODO
                break;
            // button 'A'
            case 65:
                if (app.shootMode) {
                    app.shootMode = false;
                    $(app.canvas).removeClass('shoot-cursor');
                } else {
                    app.shootMode = true;
                    $(app.canvas).addClass('shoot-cursor');
                    app.currentCharacter.model.stop();
                }
                break;
        }
        return false;   
    });
    window.addEventListener("keyup", function (e) {
        app.keys[e.keyCode] = false;
        return false;  
    });
    window.onbeforeunload = function() {
        var data = JSON.stringify({
            msg_type: 'unregister_user'
        })
        app.ws.send(data);
    };

    return app;

});