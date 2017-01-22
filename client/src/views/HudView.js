define([
    'app',
    'components/abilities',
    'backbone',
    'underscore',
    'easel',
    'tween',
], function(app, abilities, Backbone, _) {

    var size = 20,
        font = size + 'px Russo One',
        color = 'black',
        scale = 2,
        barLength = 10,
        borderSize = 675;

    return Backbone.View.extend({

        elements: [],

        /**
         * Initiate HUD border.
         */
        initBorder: function() {
            this.borderS = new createjs.Shape();
            this.borderS.graphics
                .clear()
                .setStrokeStyle(0.5)
                .beginStroke("black")
                .moveTo(0, borderSize)
                .lineTo(this.canvas.width, borderSize)
                .endStroke();

            this.elements.push(this.borderS);
        },
        /**
         * Initiate FPS text update.
         */
        initFPS: function() {
            this.textFPS = new createjs.Text();
            this.textFPS.font = font;
            this.textFPS.color = color;
            this.textFPS.x = this.canvas.width - 125;
            this.textFPS.y = 0;

            this.elements.push(this.textFPS);
            this.on('updateFPS', this.updateFPS);
        },
        /**
         * Initiate user online text update.
         */
        initOnline: function() {
            this.textOnline = new createjs.Text();
            this.textOnline.font = font;
            this.textOnline.color = color;
            this.textOnline.x = this.canvas.width - 125;
            this.textOnline.y = size;

            this.elements.push(this.textOnline);
            this.on('updateOnline', this.updateOnline);
        },
        /**
         * Initiate user volume switcher.
         */
        initMusicSwitcher: function() {
            var mutedText = (createjs.Sound.muted) ? 'Off' : 'On';
            this.textMusicSW = new createjs.Text();
            this.textMusicSW.font = font;
            this.textMusicSW.color = color;
            this.textMusicSW.text = 'Music: ' + mutedText;
            this.textMusicSW.x = this.canvas.width - 125;
            this.textMusicSW.y = 2 * size;

            this.elements.push(this.textMusicSW);
            this.textMusicSW.on('click', this.updateMusicSwitcher, this);
        },
        /**
         * Initiate user scores update.
         */
        initScores: function() {
            this.textScores = new createjs.Text();
            this.textScores.font = font;
            this.textScores.color = color;
            this.textScores.x = this.canvas.width - 125;
            this.textScores.y = 3 * size;
            this.updateScores();

            this.elements.push(this.textScores);
            this.model.on("change", this.updateScores, this);
        },
        /**
         * Initiate user drawing steps.
         */
        initSteps: function() {
            this.stepsLine = new createjs.Shape();

            this.updateSteps();
            this.elements.push(this.stepsLine);
            this.model.on("change", this.updateSteps, this);
        },
        /**
         * Initiate user AP update system.
         */
        initAP: function() {
            this.APBar = new createjs.Shape();
            this.APBar.x = size / 1.5;
            this.APBar.y = this.canvas.height - size * 2.5;

            this.updateAP();
            this.elements.push(this.APBar);
            this.model.on("change", this.updateAP, this);
        },
        /**
         * Initiate user health bar.
         */
        initHP: function() {
            this.hpBar = new createjs.Shape();
            this.hpBar.x = size / 1.5;
            this.hpBar.y = this.canvas.height - size * 3.5;

            this.updateHP();
            this.elements.push(this.hpBar);
            this.model.on("change", this.updateHP, this);
        },


        /**
         * Related updators.
         */        
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
            if (this._scores === this.model.scores) return;
            this._scores = this.model.scores;
            this.textScores.text = 'Scores: ' + this.model.scores;
        },
        updateSteps: function() {
            this.stepsLine.graphics.clear();
            this.stepsLine.graphics.setStrokeStyle(3);
            this.stepsLine.graphics.beginStroke(color);
            for (var i = 0; i < this.model.steps.length; i++) {
                var x = this.model.steps[i][0],
                    y = this.model.steps[i][1];
                this.stepsLine.graphics.lineTo(x, y);
            }
            this.stepsLine.graphics.endStroke();
        },
        updateAP: function() {
            if (this._lastAP === this.model.AP) return;

            var difMult = barLength * this.model.AP / this.model.maxAP;
            if (difMult < 0) {
                difMult = 0;
            }
            this.APBar.graphics
                .clear()
                .setStrokeStyle(0.5)
                .beginStroke("black")
                .beginFill("green")
                .drawRect(0, 0, size * difMult, 15)
                .endStroke();
            for (var i = 0; i < size * difMult; i++) {
                this.APBar.graphics
                    .setStrokeStyle(1)
                    .beginStroke("black")
                    .moveTo(size * i, 0)
                    .lineTo(size * i, 15)
                    .endStroke(); 
            }              
            this.APBar.cache(0, 0, size * difMult, 15);

            this._lastAP = this.model.AP;
        },
        updateHP: function() {
            if (this._lastHP === this.model.health) return;

            var difMult = barLength * this.model.health / this.model.maxHealth;
            if (difMult < 0) {
                difMult = 0;
            }
            this.hpBar.graphics
                .clear()
                .setStrokeStyle(0.5)
                .beginStroke("black")
                .beginFill("red")
                .drawRect(0, 0, size * difMult, 15)
                .endStroke();
            for (var i = 0; i < size * difMult; i += barLength / 4) {
                this.hpBar.graphics
                    .setStrokeStyle(1)
                    .beginStroke("black")
                    .moveTo(size * i, 0)
                    .lineTo(size * i, 15)
                    .endStroke(); 
            }              
            this.hpBar.cache(0, 0, size * difMult, 15);

            this._lastHP = this.model.health;
        },


        // MAIN
        initialize: function(args) {
            _.extend(this, Backbone.Events);

            this.stage = args.app.stage;
            this.canvas = args.app.canvas;
            this.model = args.app.currentCharacter.model;
            this.skill = abilities.Skill.create();

            this.initBorder();
            this.initFPS();
            this.initOnline();
            this.initMusicSwitcher();
            this.initScores();

            this.initAP();
            this.initHP();
            this.initSteps();

            this._renderElements();
        },
        _renderElements: function() {
            for (var i = 0; i < this.elements.length; i++) {
                this.stage.addChild(this.elements[i]);
            }
        },
        _destroyElements: function() {
            for (var i = 0; i < this.elements.length; i++) {
                this.stage.removeChild(this.elements[i]);
            }
        },
        render: function() {
            app.stage.update();
            return this;
        },
        destroy: function() {
            this._destroyElements();
            this.remove();
            this.unbind();
        }
    });

});