define([
    'app',
    'utils',
    'backbone',
    'underscore',
    'easel'
], function(app, utils, Backbone, _) {

    var cellSize = 32;

    return Backbone.View.extend({
        el: '#gameBoard',
        events: {
            click: 'onClick',
        },
        onClick: function(evt) {
            var stage = app.stage.getStage();

            if (stage.mouseY > 675) return false;
            app.currentCharacter.model.move([stage.mouseX, stage.mouseY]);
            // console.log("X: " + stage.mouseX);
            // console.log("Y: " + stage.mouseY);
        },
        onKeyUp: function(evt) {
            app.keys[evt.keyCode] = true;
            switch (evt.keyCode) {
                // button 'Z'
                case 90:
                    app.currentCharacter.model.equipWeapon();
                    break;
                // button 'H'
                case 72:
                    this._healCounter++;
                    if (this._healCounter >= 2 && (new Date() - app.modeUpdateAt) / 1000 <= 1) {
                        app.currentCharacter.model.heal();
                    }
                    if (app.modeType != 'heal') {
                        this._addMode('heal');
                    } else {
                        this._clearMods();
                    }
                    break;
                // button 'Q'
                case 81:
                    app.currentCharacter.model.stealth();
                    break;
                // button 'W'
                case 87:
                    // TODO
                    break;
                // button 'E'
                case 69:
                    // TODO
                    break;
                // button 'R'
                case 82:
                    // TODO
                    break;
                // button 'A'
                case 65:
                    if (app.modeType != 'shoot') {
                        this._addMode('shoot');
                    } else {
                        this._clearMods();
                    }
                    break;
            }
            return false;
        },
        onKeyDown: function(evt) {
            app.keys[evt.keyCode] = false;
            return false;
        },
        _addMode: function(name) {
            app.modeType = name;
            app.modeUpdateAt = new Date();
            $(app.canvas).removeClass('heal-cursor');
            $(app.canvas).removeClass('shoot-cursor');
            $(app.canvas).addClass(name + '-cursor');
            app.currentCharacter.model.stop();
        },
        _clearMods: function() {
            app.modeType = false;
            $(app.canvas).removeClass('heal-cursor');
            $(app.canvas).removeClass('shoot-cursor');
            this._healCounter = 0;
            app.modeUpdateAt = false;
        },
        // initLintBox: function() {
        //     this._highlitted = new createjs.Shape().set({alpha: 0.5});
        //     app.stage.addChild(this._highlitted);
        // },
        // canvasMouseMove: function(evt, view) {
        //     // if (evt.currentTarget instanceof createjs.Sprite) {
        //     //     console.log('FOUND')
        //     // }
        //     view.updateLintBox(evt);
        // },
        // updateLintBox: function(evt) {
        //     var cell = [evt.stageX, evt.stageY];
        //     this._highlitted.graphics.clear();
        //     this._highlitted.graphics.beginFill("red").drawRect(
        //         parseInt(cell[0] / cellSize) * cellSize,
        //         parseInt(cell[1] / cellSize) * cellSize,
        //         cellSize, cellSize
        //     );
        // },

        // // MAIN
        initialize: function() {
            window.addEventListener('keydown', this.onKeyDown.bind(this));
            window.addEventListener('keyup', this.onKeyUp.bind(this));

            this._clearMods();
        },
        destroy: function() {
            // app.stage.removeChild(this._highlitted);
            window.removeEventListener('keydown', this.onKeyDown);
            window.removeEventListener('keyup', this.onKeyUp);
            this.remove();
            this.unbind();
        }

    });

});