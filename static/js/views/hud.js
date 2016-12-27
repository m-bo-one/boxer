var app = app || {},
    utils = utils || {};

(function() {
    'use strict';

    var size = 20,
        font = size + 'px Arial',
        color = '#ff7700';

    app.HudView = Backbone.View.extend({

        el: '#gameHUD',

        initCanvas: function() {
            this.$el = $(this.el).length ? this.$el : $(this.el).appendTo('.container');
            this.canvas = this.$el[0];
            this.canvas.width = 240;
            this.canvas.height = 240;
            this.stage = new createjs.Stage(this.canvas);
        },
        initHP: function() {
            this.textHP = new createjs.Text();
            this.textHP.font = font;
            this.textHP.color = color;
            this.textHP.text = 'HP: ' + this.model.health;
            this.textHP.x = 0;
            this.textHP.y = 0;
            this.stage.addChild(this.textHP);
            this.model.on("change", this.render, this);
        },
        initFPS: function() {
            this.textFPS = new createjs.Text();
            this.textFPS.font = font;
            this.textFPS.color = color;
            this.textFPS.x = 0;
            this.textFPS.y = size;
            this.stage.addChild(this.textFPS);
            this.on('updateFPS', this.updateFPS);
        },
        initOnline: function() {
            this.textOnline = new createjs.Text();
            this.textOnline.font = font;
            this.textOnline.color = color;
            this.textOnline.x = 0;
            this.textOnline.y = 2 * size;
            this.stage.addChild(this.textOnline);
            this.on('updateOnline', this.updateOnline);
        },
        updateFPS: function(FPS) {
            this.textFPS.text = 'FPS: ' + FPS.toFixed(0);
            this.stage.update();
        },
        updateOnline: function(count) {
            this.textOnline.text = 'Online: ' + count;
            this.stage.update();
        },
        // MAIN
        initialize: function() {
            _.extend(this, Backbone.Events);
            this.initCanvas();
            this.initHP();
            this.initFPS();
            this.initOnline();
        },
        render: function() {
            this.textHP.text = 'HP: ' + this.model.health;
            this.stage.update();
            return this;
        },
        destroy: function() {
            this.stage.removeAllEventListeners();
            this.stage.removeAllChildren();
            this.remove();
            this.unbind();
            delete this.stage;
        }
    });
})();
