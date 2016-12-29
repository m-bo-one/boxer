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
            this.canvas.width = 100;
            this.canvas.height = 120;
            this.stage = new createjs.Stage(this.canvas);
        },
        initFPS: function() {
            this.textFPS = new createjs.Text();
            this.textFPS.font = font;
            this.textFPS.color = 'grey';
            this.textFPS.x = 0;
            this.textFPS.y = 0;
            this.stage.addChild(this.textFPS);
            this.on('updateFPS', this.updateFPS);
        },
        initOnline: function() {
            this.textOnline = new createjs.Text();
            this.textOnline.font = font;
            this.textOnline.color = 'grey';
            this.textOnline.x = 0;
            this.textOnline.y = size;
            this.stage.addChild(this.textOnline);
            this.on('updateOnline', this.updateOnline);
        },
        initMusicSwitcher: function() {
            var mutedText = (createjs.Sound.muted) ? 'Off' : 'On';
            this.textMusicSW = new createjs.Text();
            this.textMusicSW.font = font;
            this.textMusicSW.color = 'grey';
            this.textMusicSW.text = 'Music: ' + mutedText;
            this.textMusicSW.x = 0;
            this.textMusicSW.y = 2 * size;
            this.textMusicSW.on('click', this.updateMusicSwitcher, this);
            this.stage.addChild(this.textMusicSW);
        },
        updateFPS: function(FPS) {
            this.textFPS.text = 'FPS: ' + FPS.toFixed(0);
            this.stage.update();
        },
        updateOnline: function(count) {
            this.textOnline.text = 'Online: ' + count;
            this.stage.update();
        },
        updateMusicSwitcher: function(event) {
            createjs.Sound.muted = (createjs.Sound.muted) ? false : true;
            var mutedText = (createjs.Sound.muted) ? 'Off' : 'On';
            this.textMusicSW.text = 'Music: ' + mutedText;
            this.stage.update();
        },
        initHP: function() {
            this.initHP = new createjs.Text();
            this.initHP.font = '10 px Arial';
            this.updateHP();
            app.stage.addChild(this.initHP);
            this.model.on("change", this.updateHP, this);
        },
        updateHP: function() {
            this.initHP.text = this.model.health + '/' + 100;
            this.initHP.x = this.model.x + 5;
            this.initHP.y = this.model.y - 10;
            if (66 < this.model.health && this.model.health <= 100) {
                this.initHP.color = '#408328';
            } else if (33 < this.model.health && this.model.health <= 66) {
                this.initHP.color = '#D5D515';
            } else {
                this.initHP.color = '#990000';
            }
        },

        // MAIN
        initialize: function() {
            _.extend(this, Backbone.Events);
            this.initCanvas();
            this.initFPS();
            this.initOnline();
            this.initMusicSwitcher();
            this.initHP();
        },
        render: function() {
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
