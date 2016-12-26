var app = app || {},
    utils = utils || {};

(function() {
    'use strict';

    app.HudView = Backbone.View.extend({

        initialize: function() {
            this._text = new createjs.Text();
            this._text.font = '40px Arial';
            this._text.color = '#ff7700';
            this._text.text = 'HP: ' + this.model.health;
            this._text.x = app.canvas.width - 145;
            this._text.y -= 5;
            app.stage.addChildAt(this._text, 0);
            this.model.on("change", this.render, this);
        },
        render: function() {
            this._text.text = 'HP: ' + this.model.health;
            return this;
        },
        destroy: function() {
            app.stage.removeChild(this._text);
            this.remove();
            this.unbind();
        }
    });
})();
