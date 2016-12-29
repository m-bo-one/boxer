var app = app || {},
    utils = utils || {};

(function () {
    'use strict';

    app.UserModel = Backbone.Model.extend({

        initialize: function(options) {
            this.id = options.id;
            this.x = options.x;
            this.y = options.y;
            this.speed = options.speed;
            this.username = options.username;
            this.action = options.action;
            this.direction = options.direction;
            this.armor = options.armor;
            this.weapon = options.weapon;
            this.prevWeapon = null;
            this.health = options.health;
            this.width = options.width;
            this.height = options.height;
            this.operationsBlocked = options.operations_blocked;
            this.animation = options.animation;
            this.updatedAt = options.updated_at;
            this._options = options;

            app.users[this.id] = this;
        },
        equipedByWeapon: function() {
            return (this.weapon.name === 'no_weapon') ? false : true;
        },
        equipWeapon: function(weaponName) {
            if (this.operationsBlocked) return;
            var weaponName = weaponName || this.weapon.name;
            var data = JSON.stringify({
                msg_type: 'player_equip',
                data: {'equipment': 'weapon'}
            })
            app.ws.send(data);
        },
        isDead: function() {
            return this.health <= 0;
        },
        refreshData: function(options) {
            this._options = options;
            this.x = options.x;
            this.y = options.y;
            this.username = options.username;
            this.detected = options.detected;
            this.updatedAt = options.updated_at;

            this.health = options.health;
            this.action = options.action;
            this.direction = options.direction;

            if (options.extra_data.sound_to_play && !this.operationsBlocked) {
                createjs.Sound.play(options.extra_data.sound_to_play);
            }
            this.operationsBlocked = options.operations_blocked;

            utils._LOG('Receive update: direction - ' + options.direction + '; action - ' + options.action + '; status - ' + options.status);

            this.vision = options.vision;
            this.prevWeapon = this.weapon;
            this.weapon = options.weapon;
            this.armor = options.armor;
            this.width = options.width;
            this.height = options.height;
            this.animation = options.animation;

            this.trigger('change');
        },
        move: function(action, direction) {
            if (this.operationsBlocked || this.isDead()) return;
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
            if (this.operationsBlocked || !this.equipedByWeapon()) return;
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
            delete app.users[this.id];
            delete this;
        }
    });
})();
