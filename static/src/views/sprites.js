var app = app || {},
    utils = utils || {};

(function() {
    'use strict';

    app.SpriteView = Backbone.View.extend({

        initialize: function() {
            this.changeSprite();
            app.stage.addChild(this.model.currentSprite);
            this.model.on("change", this.render, this);
        },
        render: function() {
            this.model.currentSprite.x = this.model.x;
            this.model.currentSprite.y = this.model.y;

            if (
                this.model.prevWeapon.name != this.model.weapon.name ||
                this.model.currentSprite.currentAnimation != this.model.animation.way
            ) {
                app.stage.removeChild(this.model.currentSprite);

                this.changeSprite();

                app.stage.addChild(this.model.currentSprite);
            }
            // if (app.config.DEBUG) {
            //     this._debugBorder();
            // }
            return this;
        },
        changeSprite: function() {
            this.model.currentSprite = _.clone(app.baseSprites[this.model.animation.compound]);
            this.model.currentSprite.x = this.model.x;
            this.model.currentSprite.y = this.model.y;

            if (this.model.isDead()) {
                // play one time, hack
                this.model.currentSprite.gotoAndStop(this.model.animation.way);
                this.model.currentSprite._animation.next = false
                if (Math.floor(Date.now() / 1000) - this.model.updatedAt > 1.5) {
                    this.model.currentSprite._animation.frames.splice(0, this.model.currentSprite._animation.frames.length - 1);
                }
            }
            this.model.currentSprite.gotoAndPlay(this.model.animation.way);
            utils._LOG('Start playing animation: ' + this.model.animation.way);
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
