var app = app || {};

var utils = (function() {

    'use strict';

    return {
        getSpriteWay: function (action, direction) {
            return action + "_" + direction;
        },
        createAnimatedSprite: function (data, animKey) {
            var sh = new createjs.SpriteSheet(data.sprites[animKey]);
            var character = new createjs.Sprite(sh);

            character.x = data.x;
            character.y = data.y;
            character.width = data.sprites[animKey].frames.width;
            character.height = data.sprites[animKey].frames.height;
            character.gotoAndPlay(this.getSpriteWay(data.action, data.direction));

            return character;
        },
        _LOG: function (msg) {
            if (app.config.DEBUG) {
                console.log(msg);
            }
        }
    };
})();
