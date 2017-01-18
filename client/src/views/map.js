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
        updateLintBox: function() {
            var st = app.stage.getStage();
            var cell = [st.mouseX, st.mouseY];
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
            app.stage.on("stagemousemove", this.updateLintBox, this);
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
