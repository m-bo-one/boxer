var app = app || {},
    utils = utils || {};

(function() {
    'use strict';

    var cellSize = app.config.GAME.CELL_SIZE;

    app.MapView = Backbone.View.extend({
        sendMove: function(evt) {
            app.user.move([evt.stageX, evt.stageY]);
            console.log("X: " + evt.stageX);
            console.log("Y: " + evt.stageY);
        },
        initLintBox: function() {
            this._highlitted = new createjs.Shape().set({alpha: 0.5});
            app.stage.addChild(this._highlitted);
        },
        canvasMouseMove: function(evt, view) {
            // if (evt.currentTarget instanceof createjs.Sprite) {
            //     console.log('FOUND')
            // }
            view.updateLintBox(evt);
        },
        updateLintBox: function(evt) {
            var cell = [evt.stageX, evt.stageY];
            this._highlitted.graphics.clear();
            this._highlitted.graphics.beginFill("red").drawRect(
                parseInt(cell[0] / cellSize) * cellSize,
                parseInt(cell[1] / cellSize) * cellSize,
                cellSize, cellSize
            );
        },

        // MAIN
        initialize: function() {
            this.initLintBox();
            app.stage.on("click", this.sendMove);
            app.stage.on("stagemousemove", this.canvasMouseMove, null, false, this);
        },
        render: function() {
            app.stage.update();
            return this;
        },
        destroy: function() {
            app.stage.removeChild(this._highlitted);
            this.remove();
            this.unbind();
        }

    });
})();
