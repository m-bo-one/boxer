var app = app || {},
    utils = utils || {};

(function() {
    'use strict';

    var R, cx, cy, alphas, alphae;

    app.WeaponVisionView = Backbone.View.extend({

        initialize: function() {
            this.sshape = new createjs.Shape().set({
                x: this.model.currentSprite.x,
                y: this.model.currentSprite.y,
                visible: this.model.equipedByWeapon()
            });
            app.stage.addChild(this.sshape);
            this.model.on("change", this.render, this);
        },
        render: function() {
            this.sshape.x = this.model.currentSprite.x;
            this.sshape.y = this.model.currentSprite.y;

            R = this.model.vision.R;
            alphas = this.model.vision.alphas;
            alphae = this.model.vision.alphae;
            cx = this.model.width / 2;
            cy = this.model.height / 2;

            this.sshape.graphics.clear();
            this.sshape.graphics.s("#f00")
            this.sshape.graphics.ss(0.75);
            this.sshape.graphics.setStrokeDash([5, 5]);
            this.sshape.graphics.moveTo(cx, cy);
            this.sshape.graphics.arc(cx, cy, R, utils.toRadians(alphas), utils.toRadians(alphae));
            this.sshape.graphics.lt(cx, cy);
            this.sshape.graphics.endFill();

            this.sshape.visible = this.model.equipedByWeapon();

            return this
        },
        destroy: function() {
            app.stage.removeChild(this.sshape);
            this.remove();
            this.unbind();
        }
    });
})();
