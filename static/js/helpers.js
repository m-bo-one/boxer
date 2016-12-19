var app = app || {};
var utils = (function() {
    'use strict';

    var createAnimatedSprite = function (data, animKey) {

        var sh = new createjs.SpriteSheet(data.sprites[animKey]);
        var character = new createjs.Sprite(sh);
        character.x = data.x;
        character.y = data.y;
        character.width = data.sprites[animKey].frames.width;
        character.height = data.sprites[animKey].frames.height;
        character.gotoAndPlay(getSpriteWay(data.action, data.direction));

        return character;
    };

    var getSpriteWay = function (action, direction) {
        return action + "_" + direction;
    };

    var _LOG = function (msg) {
        if (app.config.DEBUG) console.log(msg);
    };

    return {
        getSpriteWay: getSpriteWay,
        createAnimatedSprite: createAnimatedSprite,
        _LOG: _LOG
    };

})();
