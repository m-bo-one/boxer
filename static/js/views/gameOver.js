var app = app || {},
    utils = utils || {};

(function() {
    'use strict';

    app.GameOverView = Backbone.View.extend({

        initialize: function() {
            this._text = new createjs.Text();
            this._text.visible = false;
            this._text.font = '40px Arial';
            this._text.color = '#ff7700';
            this._text.text = 'GAME OVER!';
            this._text.x = (app.canvas.width / 2) - 100;
            this._text.y = app.canvas.height / 2;
            app.stage.addChildAt(this._text, 0);
            this.model.on("change", this.render, this);
        },
        render: function() {
            if (this.model.health > 0) {
                this._text.visible = false;
                return;
            }
            console.log('Game over!');
            var data = JSON.stringify({
                msg_type: 'unregister_user'
            });
            app.ws.send(data);
            this._text.visible = true;
            return this;
        },
        destroy: function() {
            app.stage.removeChild(this._text);
            this.remove();
            this.unbind();
        }
    });
})();
