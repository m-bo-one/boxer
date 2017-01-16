var app = app || {},
    utils = utils || {};

(function() {
    'use strict';

    var size = 20,
        font = size + 'px Russo One',
        color = 'black',
        scale = 2;

    app.HudView = Backbone.View.extend({

        initFPS: function() {
            this.textFPS = new createjs.Text();
            this.textFPS.font = font;
            this.textFPS.color = color;
            this.textFPS.x = app.canvas.width - 125;
            this.textFPS.y = 0;
            app.stage.addChild(this.textFPS);
            this.on('updateFPS', this.updateFPS);
        },
        initOnline: function() {
            this.textOnline = new createjs.Text();
            this.textOnline.font = font;
            this.textOnline.color = color;
            this.textOnline.x = app.canvas.width - 125;
            this.textOnline.y = size;
            app.stage.addChild(this.textOnline);
            this.on('updateOnline', this.updateOnline);
        },
        initMusicSwitcher: function() {
            var mutedText = (createjs.Sound.muted) ? 'Off' : 'On';
            this.textMusicSW = new createjs.Text();
            this.textMusicSW.font = font;
            this.textMusicSW.color = color;
            this.textMusicSW.text = 'Music: ' + mutedText;
            this.textMusicSW.x = app.canvas.width - 125;
            this.textMusicSW.y = 2 * size;
            this.textMusicSW.on('click', this.updateMusicSwitcher, this);
            app.stage.addChild(this.textMusicSW);
        },
        initScores: function() {
            this.textScores = new createjs.Text();
            this.textScores.font = font;
            this.textScores.color = color;
            this.textScores.x = app.canvas.width - 125;
            this.textScores.y = 3 * size;
            this.updateScores();
            this.model.on("change", this.updateScores, this);
            app.stage.addChild(this.textScores);
        },
        initAP: function() {
            this.imageActiveAP = [];
            this.model.on("action", this.updateAP, this);
            this.updateAP();
        },
        initSteps: function() {
            this.stepsLine = new createjs.Shape();
            this.model.on("change", this.updateSteps, this);
            this.updateSteps();
            app.stage.addChild(this.stepsLine);
        },
        updateFPS: function(FPS) {
            this.textFPS.text = 'FPS: ' + FPS.toFixed(0);
        },
        updateOnline: function(count) {
            this.textOnline.text = 'Online: ' + count;
        },
        updateMusicSwitcher: function(event) {
            createjs.Sound.muted = (createjs.Sound.muted) ? false : true;
            var mutedText = (createjs.Sound.muted) ? 'Off' : 'On';
            this.textMusicSW.text = 'Music: ' + mutedText;
        },
        updateScores: function() {
            this.textScores.text = 'Scores: ' + this.model.scores;
        },
        updateAP: function() {
            var dist = 0,
                cAP = this.imageActiveAP.slice();
            this.imageActiveAP = [];
            for (var j = 0; j < cAP.length; j++) {
                app.stage.removeChild(cAP[j]);
            }
            for (var i = 0; i < this.model.AP; i++) {
                var img = app.baseImages['active_AP'].clone();
                img.scaleX = scale;
                img.scaleY = scale;
                img.x += (size) / 1.5 + dist;
                img.y += app.canvas.height - size * 3 / 2;
                app.stage.addChildAt(img, app.stage.numChildren - 1);
                this.imageActiveAP.push(img);
                dist += size;
            }
        },
        updateSteps: function() {
            this.stepsLine.graphics.clear();
            this.stepsLine.graphics.setStrokeStyle(3);
            this.stepsLine.graphics.beginStroke(color);
            // this.stepsLine.graphics.moveTo(0, 0);
            for (var i = 0; i < this.model.steps.length; i++) {
                var x = this.model.steps[i][0],
                    y = this.model.steps[i][1];
                this.stepsLine.graphics.lineTo(x, y);
            }
            this.stepsLine.graphics.endStroke();
        },

        // MAIN
        initialize: function() {
            _.extend(this, Backbone.Events);
            this.panelLeft();
            this.panelRight();
        },
        panelRight: function() {
            this.initFPS();
            this.initOnline();
            this.initMusicSwitcher();
            this.initScores();
        },
        panelLeft: function() {
            this.initAP();
            this.initSteps();
        },
        render: function() {
            app.stage.update();
            return this;
        },
        destroy: function() {
            this.remove();
            this.unbind();
            app.stage.removeChild(this.stepsLine);
        }
    });
})();
