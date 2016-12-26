var app = app || {},
    utils = utils || {};

(function () {
    'use strict';

    app.UserModel = Backbone.Model.extend({

        initialize: function(options) {
            this.id = options.id;
            this.speed = options.speed;
            this.username = options.username;
            this.action = options.action;
            this.direction = options.direction;
            this.armor = options.armor;
            this.weapon = options.weapon;
            this.health = options.health;
            this.vision = options.vision;

            this.loadSprites(options);

            this.width = options.width;
            this.height = options.height;

            app.users[this.id] = this;
        },
        equipedByWeapon: function() {
            return (this.weapon === 'no_weapon') ? false : true;
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
            this.health = options.health;
            if (this.health <= 0) {
                console.log('Game over!');
                return;
            }

            this.currentSprite.x = options.x;
            this.currentSprite.y = options.y;

            this.action = options.action;
            this.direction = options.direction;

            utils._LOG('Receive update: direction - ' + options.direction + '; action - ' + options.action);

            this.vision = options.vision;

            var way = utils.getSpriteWay(options.action, options.direction);

            if (this.weapon != options.weapon || this.currentSprite.currentAnimation != way) {
                app.stage.removeChild(this.currentSprite);

                this.weapon = options.weapon;
                this.armor = options.armor;
                this.width = options.width;
                this.height = options.height;

                this.changeSprite();

                this.currentSprite.x = options.x;
                this.currentSprite.y = options.y;

                utils._LOG('Start playing animation: ' + way);
                this.currentSprite.gotoAndPlay(way);

                app.stage.addChild(this.currentSprite);
            }

            this.trigger('change');
        },
        move: function(action, direction) {
            utils._LOG('Send move: direction - ' + direction + '; action - ' + action);
            var data = JSON.stringify({
                msg_type: 'player_move',
                data: {
                    'action': action,
                    'direction': direction
                }
            });
            app.ws.send(data);
        },
        shoot: function () {
            var data = JSON.stringify({
                msg_type: 'player_shoot',
                data: {}
            });
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
