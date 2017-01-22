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
            console.log("X: " + stage.mouseX);
            console.log("Y: " + stage.mouseY);
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
                    if (!app.modeType) {
                        app.modeType = 'heal';
                        $(app.canvas).addClass('heal-cursor');
                        app.currentCharacter.model.stop();
                    } else {
                        app.modeType = false;
                        $(app.canvas).removeClass('heal-cursor');
                    }
                    // app.currentCharacter.model.heal();
                    break;
                // button 'Q'
                case 81:
                    // app.currentCharacter.model.stealth();
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
                    if (!app.modeType) {
                        app.modeType = 'shoot';
                        $(app.canvas).addClass('shoot-cursor');
                        app.currentCharacter.model.stop();
                    } else {
                        app.modeType = false;
                        $(app.canvas).removeClass('shoot-cursor');
                    }
                    break;
            }
            return false;
        },
        onKeyDown: function(evt) {
            app.keys[evt.keyCode] = false;
            return false;
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
            window.addEventListener('keydown', this.onKeyDown);
            window.addEventListener('keyup', this.onKeyUp);

            app.modeType = false;
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