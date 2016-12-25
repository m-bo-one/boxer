var app = app || {},
    utils = utils || {};

(function() {
    'use strict';

    var R, cx, cy, alphas, alphae;

    app.WeaponVisionView = Backbone.View.extend({

        el: 'canvas',

        initialize: function(options) {
            this.sshape = new createjs.Shape().set({
                x: options.x,
                y: options.y,
                visible: false
            });
            this.render(options);
        },

        render: function(options) {

            this._drawByDirection(options);

            app.stage.addChild(this.sshape);
            return this.sshape;
        },

        _drawByDirection: function(options) {
            R = options.vision.R;
            alphas = alphae = options.vision.alpha;
            cx = options.width / 2;
            cy = options.height / 2;

            this.sshape.graphics.clear();
            this.sshape.graphics.s("#f00").ss(1);

            switch (options.direction) {
                case 'left':
                    alphas = 180 - alphas;
                    alphae = 180 + alphae;
                    break;
                case 'right':
                    alphas = -alphas;
                    break;
                case 'top':
                    alphas = -90 - alphas;
                    alphae = -90 + alphae;
                    break;
                case 'bottom':
                    alphas = 90 - alphas;
                    alphae = 90 + alphae;
                    break;
            }

            this.sshape.graphics.moveTo(cx, cy);
            this.sshape.graphics.arc(cx, cy, R, utils.toRadians(alphas), utils.toRadians(alphae));
            this.sshape.graphics.lt(cx, cy)            
        },

        update: function(options) {
            this.sshape.x = options.x;
            this.sshape.y = options.y;

            this._drawByDirection(options);

            this.sshape.visible = (options.weapon === 'no_weapon') ? false : true;
        },
    });
})();
