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
            this.loadSprites();

            app.users[this.id] = this;
        },
        loadSprites: function(sprites) {
            this.sprites = {}
            for (var compound_key in sprites) {
                var data = {}
                data.sprite = sprites[compound_key];
                data.x = this.x;
                data.y = this.y;
                data.action = this.action;
                data.direction = this.direction;
                this.sprites[compound_key] = createAnimatedSprite(app.stage, sprites[compound_key]);
            }
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
            this.move("idle", this.direction);
        },
        destroy: function() {
            app.stage.removeChild(this.sprite);
            delete this;
        }
    });
})();