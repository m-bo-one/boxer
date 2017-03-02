define(['config', 'jquery', 'backbone', 'easel'], function(config, $, Backbone) {

    var gameLoop = function (event) {
        app.stage.update();
        if (app.currentCharacter) {
            app.currentCharacter.hud.trigger('updateFPS', createjs.Ticker.getMeasuredFPS());
        }

    };

    window.app = {};
    app.keys = {};
    app.characters = {};
    app.turrets = {};
    app.tilesets = {};
    app.shootMode = false;
    app.currentCharacter = null;

    app.config = config;

    app.canvas = document.getElementById("gameBoard");
    app.canvas.width = app.config.BOARD.width;
    app.canvas.height = app.config.BOARD.height;
    app.canvas.style.backgroundColor = "white";
    app.ctx = app.canvas.getContext("2d");
    app.stage = new createjs.Stage(app.canvas);
    app.stage.enableMouseOver(10);

    createjs.Ticker.addEventListener("tick", gameLoop);
    createjs.Ticker.setFPS(app.config.FPS);

    return app;

});