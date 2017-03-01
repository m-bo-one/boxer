require([
    'app',
    'utils',
    'stream',
    'backbone',
    'underscore',
    'easel',
    'sound'
], function(app, utils, Stream, Backbone, _) {

    app.TurretModel = Backbone.Model.extend({

        initialize: function(data) {
            this.id = data.id;
            this.R = data.R;
            if (app.characters[data.target]) {
                this.target = app.characters[data.target].model;
            } else {
                this.target = null;
            }
            this.x = data.x;
            this.y = data.y;
            this.shape = new createjs.Shape();
            this.shape.graphics
                .clear()
                .setStrokeStyle(0.5)
                .beginStroke("black")
                .drawCircle(this.x, this.y, this.R)
                .endStroke();
            app.stage.addChild(this.shape);

            this.line = new createjs.Shape();
            app.stage.addChild(this.line);

            this.music = null;
        },

        _musicRepeater: function() {
            if (this.music) return;
            var self = this;
            this.music = createjs.Sound.play('fire');
            this.music.addEventListener("complete", function(instance) {
                if (self.music) self.music.removeAllEventListeners();
                self._musicRepeater();
            });
        },

        refreshData: function(data) {
            if (app.characters[data.target]) {
                this.target = app.characters[data.target].model;
                this.line.graphics
                    .clear()
                    .setStrokeStyle(0.5)
                    .beginStroke("black")
                    .moveTo(this.x, this.y)
                    .lineTo(this.target.x, this.target.y)
                    .endStroke();

                // this._musicRepeater();
            } else {
                this.target = null;
                this.line.graphics.clear();
            }
        }

    });

});