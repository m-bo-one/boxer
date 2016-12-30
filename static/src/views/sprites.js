var app = app || {},
    utils = utils || {};

(function() {
    'use strict';

    var _stars, _hpColor,
        size = 10;

    app.SpriteView = Backbone.View.extend({

        initialize: function() {
            this.changeSprite();
            this.initUsername();
            this.initHP();
            this.model.on("change", this.render, this);
        },
        render: function() {
            this.model.currentSprite.x = this.model.x;
            this.model.currentSprite.y = this.model.y;

            if (
                this.model.prevWeapon.name != this.model.weapon.name ||
                this.model.currentSprite.currentAnimation != this.model.animation.way
            ) {
                this.changeSprite();
            }
            // if (app.config.DEBUG) {
                // this._debugBorder();
            // }
            this.updateUsername();
            this.updateHP();
            return this;
        },
        changeSprite: function() {
            if (this.model.currentSprite) app.stage.removeChild(this.model.currentSprite);

            this.model.currentSprite = _.clone(app.baseSprites[this.model.animation.compound]);
            this.model.currentSprite.x = this.model.x;
            this.model.currentSprite.y = this.model.y;

            if (this.model.isDead()) {
                // play one time, hack
                this.model.currentSprite.gotoAndStop(this.model.animation.way);
                this.model.currentSprite._animation.next = false;
                if (Math.floor(Date.now() / 1000) - this.model.updatedAt > 2) {
                    this.model.currentSprite._animation.frames.splice(0, this.model.currentSprite._animation.frames.length - 1);
                }
            }
            if (this.model.action == 'idle') {
                this.model.currentSprite.gotoAndStop(this.model.animation.way);
            } else {
                this.model.currentSprite.gotoAndPlay(this.model.animation.way);
            }
            utils._LOG('Start playing animation: ' + this.model.animation.way);

            app.stage.addChild(this.model.currentSprite);
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
        initUsername: function() {
            this.textUsername = new createjs.Text();
            this.textUsername.font = size + ' px Arial';
            this.updateUsername();
            app.stage.addChild(this.textUsername);
        },
        updateUsername: function() {
            this.textUsername.text = this.model.username;
            this.textUsername.x = this.model.x + size / 1.5 - this.model.username.length;
            this.textUsername.y = this.model.y - size;
        },
        initHP: function() {
            this.initHP = new createjs.Text();
            this.initHP.font = size + ' px Arial';
            this.updateHP();
            app.stage.addChild(this.initHP);
        },
        updateHP: function() {
            if (this.model.health == 100) {
                _hpColor = '#156526';
                _stars = ' * '.repeat(4);
            } else if (66 < this.model.health && this.model.health <= 100) {
                _hpColor = '#1de592';
                _stars = ' * '.repeat(3);
            } else if (33 < this.model.health && this.model.health <= 66) {
                _hpColor = '#FF7400';
                _stars = ' * '.repeat(2);
            } else if (0 < this.model.health && this.model.health <= 33) {
                _hpColor = '#990000';
                _stars = ' * '.repeat(1);
            } else {
                _hpColor = '#990000';
                _stars = '-';
            }

            this.initHP.color = _hpColor;

            if (this.model == app.user) {
                this.initHP.text = this.model.health + '/' + 100;
                this.initHP.x = this.model.x + size - this.initHP.text.length;
                this.initHP.y = this.model.y - 2 * size;
            } else {
                this.initHP.text = _stars;
                this.initHP.x = this.model.x + size - this.initHP.text.length;
                this.initHP.y = this.model.y - 2 * size;
            }
        },
        destroy: function() {
            app.stage.removeChild(this.textUsername);
            app.stage.removeChild(this.initHP);
            this.remove();
            this.unbind();
            delete app.sprites[this.model.id];
        }
    });
})();
