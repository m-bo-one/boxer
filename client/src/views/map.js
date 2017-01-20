require([
    'app',
    'utils',
    'backbone',
    'underscore',
    'easel'
], function(app, utils, Backbone, _) {

    var cellSize = 32;

    app.MapView = Backbone.View.extend({
        el: '#gameBoard',
        events: {
            'click': 'sendMove'
        },
        sendMove: function(evt) {
            var stage = app.stage.getStage();
            app.currentCharacter.model.move([stage.mouseX, stage.mouseY]);
            console.log("X: " + stage.mouseX);
            console.log("Y: " + stage.mouseY);
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

        },
        destroy: function() {
            app.stage.removeChild(this._highlitted);
            this.remove();
            this.unbind();
        }

    });

});