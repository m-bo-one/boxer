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
            this.prevWeapon = null;
            this.health = options.health;
            this.vision = options.vision;
            this.width = options.width;
            this.height = options.height;
            this._sprites = {}
            this._options = options;

            app.users[this.id] = this;
        },
        equipedByWeapon: function() {
            return (this.weapon === 'no_weapon') ? false : true;
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
            this._options = options;

            this.health = options.health;
            if (this.health <= 0) {
                console.log('Game over!');
                return;
            }
            this.action = options.action;
            this.direction = options.direction;

            utils._LOG('Receive update: direction - ' + options.direction + '; action - ' + options.action);

            this.vision = options.vision;
            this.prevWeapon = this.weapon;
            this.weapon = options.weapon;
            this.armor = options.armor;
            this.width = options.width;
            this.height = options.height;

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
