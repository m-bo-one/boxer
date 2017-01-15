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
            this.name = options.name;
            this.action = options.action;
            this.direction = options.direction;
            this.armor = options.armor;
            this.weapon = options.weapon;
            this.prevWeapon = null;
            this.health = options.health;
            // this.width = options.width;
            // this.height = options.height;
            this.operationsBlocked = options.operations_blocked;
            this.animation = options.animation;
            this.updatedAt = options.updated_at;
            this.scores = options.scores;
            this.maxHealth = options.max_health;
            this.AP = options.AP;
            this.maxAP = options.max_AP;
            // this.pivot = options.pivot;
            this._options = options;
            this._APCallbacks = [];

            app.users[this.id] = this;
        },
        equipedByWeapon: function() {
            return (this.weapon === 1) ? false : true;
        },
        equipWeapon: function(weaponName) {
            if (this.operationsBlocked) return;
            var weaponName = weaponName || this.weapon.name;
            Stream.send('player_equip', {'equipment': 'weapon'});
        },
        isDead: function() {
            return this.health <= 0;
        },
        isFullHealth: function() {
            return this.health == this.maxHealth;
        },
        refreshData: function(options) {
            this._options = options;
            this.x = options.x;
            this.y = options.y;
            this.name = options.name;
            this.detected = options.detected;
            this.updatedAt = options.updated_at;
            this.scores = options.scores;

            this.health = options.health;
            this.action = options.action;
            this.direction = options.direction;
            this.maxAP = options.max_AP;

            if (!this.operationsBlocked && options.hasOwnProperty('extra_data') && options.extra_data.sound_to_play) {
                setTimeout(function() {
                    createjs.Sound.play(options.extra_data.sound_to_play);
                }, 200);
            }
            this.operationsBlocked = options.operations_blocked;

            utils._LOG('Receive update: direction - ' + options.direction + '; action - ' + options.action + ';');

            this.vision = options.vision;
            this.prevArmor = this.armor;
            this.weapon = options.weapon;
            this.armor = options.armor;
            // this.width = options.width;
            // this.height = options.height;
            this.animation = options.animation;
            this.AP = options.AP;
            // this.pivot = options.pivot;

            // if (app.user.id == this.id && options.extra_data.resurection_time) {
            //     // TODO: Dont know where resurect timer need to show( End it in future
            //     utils.startTimer(options.extra_data.resurection_time);
            // }

            this.trigger('change');
            if (this.AP !== this.maxAP) {
                this.trigger('action');
            }
        },
        move: function(action, direction) {
            if (this.operationsBlocked || this.isDead()) return;
            utils._LOG('Send move: direction - ' + direction + '; action - ' + action);
            Stream.send('player_move', {
                'action': action,
                'direction': direction
            });
        },
        shoot: function () {
            if (this.operationsBlocked || !this.equipedByWeapon() || this.AP < 5) return;
            Stream.send('player_shoot');
        },
        heal: function () {
            if (this.operationsBlocked || this.isDead() || this.isFullHealth()  || this.AP < 4) return;
            Stream.send('player_heal');
        },
        stop: function() {
            this.move(app.constants.Action.Breathe, this.direction);
        },
        destroy: function() {
            app.stage.removeChild(this.currentSprite);
            delete app.users[this.id];
            delete this;
        }
    });
})();
