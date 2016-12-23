var app = app || {},
    utils = utils || {};

(function () {
    'use strict';

    app.UserModel = Backbone.Model.extend({

        defaults: {
            id: null,
            speed: null,
            username: null,
            action: null,
            direction: null,
            sprites: null
        },
        initialize: function(options) {
            this.id = options.id;
            this.speed = options.speed;
            this.username = options.username;
            this.action = options.action;
            this.direction = options.direction;
            this.armor = options.armor;
            this.weapon = options.weapon;
            this.health = options.health;

            this.loadSprites(options);

            this.width = options.width;
            this.height = options.height;

            app.users[this.id] = this;
        },
        loadSprites: function(options) {
            this._sprites = {}
            for (var compoundKey in options.sprites) {
                this._sprites[compoundKey] = utils.createAnimatedSprite(options, compoundKey);
            }
            this.changeSprite();
            app.stage.addChild(this.currentSprite);
        },
        changeSprite: function(compoundKey) {
            compoundKey = compoundKey || [this.armor, this.weapon, this.action].join(':');;
            this.currentSprite = this._sprites[compoundKey];
        },
        equipWeapon: function(weaponName) {
            var weaponName = weaponName || this.weapon;
            var data = JSON.stringify({
                msg_type: 'player_equip',
                data: {'equipment': 'weapon'}
            })
            app.ws.send(data);
        },
        refreshData: function(options) {
            utils._LOG('Receive update: direction - ' + options.direction + '; action - ' + options.action);
            this.currentSprite.x = options.x;
            this.currentSprite.y = options.y;
            this.health = options.health;
            this.width = options.width;
            this.height = options.height;

            var way = utils.getSpriteWay(options.action, options.direction);

            if (this.health <= 0) {
                console.log('Game over!');
                return;
            }

            if (this.currentSprite.currentAnimation != way) {
                app.stage.removeChild(this.currentSprite);

                this.action = options.action;
                this.direction = options.direction;
                this.weapon = options.weapon;
                this.armor = options.armor;

                this.changeSprite();

                this.currentSprite.x = options.x;
                this.currentSprite.y = options.y;

                utils._LOG('Start playing animation: ' + way);
                this.currentSprite.gotoAndPlay(way);

                app.stage.addChild(this.currentSprite);
            }
        },
        move: function(action, direction) {
            utils._LOG('Send move: direction - ' + direction + '; action - ' + action);
            var data = JSON.stringify({
                msg_type: 'player_move',
                data: {
                    'action': action,
                    'direction': direction
                }
            })
            app.ws.send(data);
        },
        shoot: function () {
            var data = JSON.stringify({
                msg_type: 'player_shoot',
                data: {}
            })
            app.ws.send(data);
        },
        stop: function() {
            this.move("idle", this.direction);
        },
        destroy: function() {
            app.stage.removeChild(this.currentSprite);
            delete this;
        }
    });
})();
