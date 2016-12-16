var app = app || {};

(function () {
    'use strict';

    app.UserModel = Backbone.Model.extend({

        defaults: {
            id: null,
            speed: null,
            username: null,
            action: null,
            direction: null,
            sprite: null
        },
        initialize: function(options) {
            this.id = options.id;
            this.speed = options.speed;
            this.username = options.username;

            this.action = options.action;
            this.direction = options.direction;
            this.sprite = createAnimatedSprite(app.stage, options);

            app.users[this.id] = this;
        },
        update: function(options) {
            this.sprite.x = options.x;
            this.sprite.y = options.y;

            var way = getWay(options.action, options.direction);
            if (this.sprite.currentAnimation != way) {
                this.action = options.action;
                this.direction = options.direction;
                this.sprite.gotoAndPlay(way);
            }            
        },
        move: function(action, direction) {
            var data = JSON.stringify({
                msg_type: 'player_move',
                data: {
                    'id': this.id,
                    'action': action,
                    'direction': direction
                }
            })
            app.ws.send(data);            
        },
        stop: function() {
            this.move("wait", this.direction);
        },
        destroy: function() {
            app.stage.removeChild(this.sprite);
            delete this;
        }
    });
})();