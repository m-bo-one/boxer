var app = app || {},
    utils = utils || {};

(function() {
    'use strict';

    var compoundKey, way;

    app.SpriteView = Backbone.View.extend({

        el: 'canvas',

        initialize: function() {
            for (var compoundKey in this.model._options.sprites) {
                this.model._sprites[compoundKey] = this.createAnimatedSprite(compoundKey);
            }
            this.changeSprite();
            app.stage.addChild(this.model.currentSprite);
            this.model.on("change", this.render, this);
        },
        render: function() {
            this.model.currentSprite.x = this.model._options.x;
            this.model.currentSprite.y = this.model._options.y;

            way = this.getWay();

            if (
                this.model.prevWeapon != this.model.weapon ||
                this.model.currentSprite.currentAnimation != way
            ) {
                app.stage.removeChild(this.model.currentSprite);

                this.changeSprite();

                this.model.currentSprite.x = this.model._options.x;
                this.model.currentSprite.y = this.model._options.y;

                utils._LOG('Start playing animation: ' + way);
                this.model.currentSprite.gotoAndPlay(way);

                app.stage.addChild(this.model.currentSprite);
            }
            return this;
        },
        getWay: function() {
            return [this.model.action, this.model.direction].join('_');
        },
        getCompoundKey: function() {
            return [this.model.armor, this.model.weapon, this.model.action].join(':');
        },
        createAnimatedSprite: function(animKey) {
            var sh = new createjs.SpriteSheet(this.model._options.sprites[animKey]);
            var character = new createjs.Sprite(sh);

            character.x = this.model._options.x;
            character.y = this.model._options.y;
            character.width = this.model._options.sprites[animKey].frames.width;
            character.height = this.model._options.sprites[animKey].frames.height;
            character.gotoAndPlay(this.getWay());

            return character;
        },
        changeSprite: function() {
            this.model.currentSprite = this.model._sprites[this.getCompoundKey()];
        },
    });
})();
