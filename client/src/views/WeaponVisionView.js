define([
    'app',
    'utils',
    'backbone',
    'underscore'
], function(app, utils, Backbone, _) {

    var R, cx, cy, alphas, alphae, size;

    return Backbone.View.extend({

        initialize: function(args) {
            this.stage = args.app.stage;
            this.canvas = args.app.canvas;
            this.model = args.app.currentCharacter.model;
            this.sshape = new createjs.Shape().set({
                x: this.model.currentSprite.x,
                y: this.model.currentSprite.y,
                visible: this.model.needToShowVision()
            });
            this.stage.addChild(this.sshape);
            this.model.on("change", this.render, this);
        },
        recalSize: function() {
            if (this.model.equipedByWeapon() && !this._recalled) {
                size = this.model.currentSprite.getBounds();
                this.cx = parseInt(size.width / 2);
                this.cy = parseInt(size.height / 2);
                this._recalled = true;             
            } else {
                this._recalled = false;
            }
        },
        render: function() {
            this.sshape.x = this.model.currentSprite.x;
            this.sshape.y = this.model.currentSprite.y;

            R = this.model.weapon_range;

            this.recalSize();
            // size = this.model.currentSprite.getBounds();
            // cx = size.width / 2;
            // cy = size.height / 2;
            // console.log(this.cx, this.cy);
            this.sshape.graphics
                .clear()
                .setStrokeStyle(0.5)
                .beginStroke("red")
                .drawCircle(this.cx, this.cy, R)
                .endStroke();

            this.sshape.visible = this.model.needToShowVision();

            return this;
        },
        destroy: function() {
            this.stage.removeChild(this.sshape);
            this.remove();
            this.unbind();
        }
    });

});