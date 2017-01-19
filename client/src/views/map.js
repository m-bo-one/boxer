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
            'click': 'sendMove',
            'mouseover': 'cursorUpdate',
            'mouseout': 'cursorKill'
        },
        sendMove: function(evt) {
            var stage = app.stage.getStage();
            app.currentCharacter.model.move([stage.mouseX, stage.mouseY]);
            console.log("X: " + stage.mouseX);
            console.log("Y: " + stage.mouseY);
        },
        cursorUpdate: function(evt) {
            if (app.shootMode) {
                this.$el.css('cursor', 'url(/assets/attack_cursor.png), auto;');
            }
        },
        cursorKill: function(evt) {
            if (!app.shootMode) {
                this.$el.css('cursor', 'auto');
            }
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
        // initialize: function() {
        //     // this.initLintBox();
        //     // app.stage.on("click", this.sendMove);
        //     // app.stage.on("stagemousemove", this.canvasMouseMove, null, false, this);
        // },
        // render: function() {
        //     // app.stage.update();
        //     return this;
        // },
        destroy: function() {
            app.stage.removeChild(this._highlitted);
            this.remove();
            this.unbind();
        }

    });

});