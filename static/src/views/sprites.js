var app = app || {},
    utils = utils || {};

(function() {
    'use strict';

    var compoundKey, way;

    app.SpriteView = Backbone.View.extend({

        initialize: function() {
            this.changeSprite();
            app.stage.addChild(this.model.currentSprite);
            this.model.on("change", this.render, this);
        },
        render: function() {
            this.model.currentSprite.x = this.model.x;
            this.model.currentSprite.y = this.model.y;

            way = this.getWay();

            if (
                this.model.prevWeapon != this.model.weapon ||
                this.model.currentSprite.currentAnimation != way
            ) {
                app.stage.removeChild(this.model.currentSprite);

                this.changeSprite();

                app.stage.addChild(this.model.currentSprite);
            }
            if (app.config.DEBUG) {
                this._debugBorder();
            }
            return this;
        },
        getWay: function() {
            return [this.model.action, this.model.direction].join('_');
        },
        getCompoundKey: function() {
            return [this.model.armor, this.model.weapon, this.model.action].join('-');
        },
        changeSprite: function(way) {
            way = way || this.getWay();
            this.model.currentSprite = _.clone(app.baseSprites[this.getCompoundKey()]);
            this.model.currentSprite.x = this.model.x;
            this.model.currentSprite.y = this.model.y;
            utils._LOG('Start playing animation: ' + way);
            this.model.currentSprite.gotoAndPlay(way);
        },
        _debugBorder: function() {
            if (this.sshape) {
                app.stage.removeChild(this.sshape);
            }
            this.sshape = new createjs.Shape().set({
                x: this.model.currentSprite.x,
                y: this.model.currentSprite.y
            });
            this.sshape.graphics.clear();
            this.sshape.graphics.ss(1);
            this.sshape.graphics.beginStroke("#000000");
            this.sshape.graphics.moveTo(0, 0);
            this.sshape.graphics.lineTo(this.model.width, 0);
            this.sshape.graphics.lineTo(this.model.width, this.model.height);
            this.sshape.graphics.lineTo(0, this.model.height);
            this.sshape.graphics.lineTo(0, 0);
            this.sshape.graphics.endFill();
            // this.sshape.graphics.drawRect(0, 0, this.model.width, this.model.height);
            app.stage.addChild(this.sshape);
        },
        destroy: function() {
            this.remove();
            this.unbind();
        }
    });
})();
