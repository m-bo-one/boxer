require([
    'app',
    'utils',
    'stream',
    'backbone',
    'underscore',
    'easel',
    'sound'
], function(app, utils, Stream, Backbone, _) {

    app.CharacterModel = Backbone.Model.extend({

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
            this.operationsBlocked = options.operations_blocked;
            this.animation = options.animation;
            this.updatedAt = options.updated_at;
            this.scores = options.scores;
            this.maxHealth = options.max_health;
            this.AP = options.AP;
            this.maxAP = options.max_AP;
            this.steps = options.steps;
            this.display = options.display;
            this.weapon_range = options.weapon_range;
            this._options = options;
            this._APCallbacks = [];
        },
        equipedByWeapon: function() {
            return (this.weapon === 1) ? false : true;
        },
        equipWeapon: function(weaponName) {
            if (this.operationsBlocked) return;
            weaponName = weaponName || this.weapon.name;
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
            this.weapon_range = options.weapon_range;

            this.health = options.health;
            this.action = options.action;
            this.direction = options.direction;
            this.maxAP = options.max_AP;
            this.steps = options.steps;

            if (!this.operationsBlocked && options.hasOwnProperty('extra_data') && options.extra_data.sound_to_play) {
                setTimeout(function() {
                    createjs.Sound.play(options.extra_data.sound_to_play);
                }, 300);
            }
            this.operationsBlocked = options.operations_blocked;

            utils._LOG('Receive update: direction - ' + options.direction + '; action - ' + options.action + ';');

            this.vision = options.vision;
            this.weapon = options.weapon;
            this.armor = options.armor;
            this.animation = options.animation;
            this.AP = options.AP;
            this.display = options.display;

            // if (app.user.id == this.id && options.extra_data.resurection_time) {
            //     // TODO: Dont know where resurect timer need to show( End it in future
            //     utils.startTimer(options.extra_data.resurection_time);
            // }

            this.trigger('change');
            if (this.AP <= this.maxAP) {
                this.trigger('action');
            }
        },
        actionModeEnabled: function() {
            return (app.modeType !== false);
        },
        shootModeEnabled: function() {
            return (app.modeType == 'shoot');
        },
        healModeEnabled: function() {
            return (app.modeType == 'heal');
        },
        move: function(point) {
            if (this.actionModeEnabled() || this.operationsBlocked || this.isDead()) return;
            Stream.send('player_move', {'point': point});
        },
        stealth: function() {
            if (this.isDead()) return;
            Stream.send('player_stealth');
        },
        shoot: function(cid) {
            if (!this.shootModeEnabled() || this.operationsBlocked ||
                !this.equipedByWeapon() || this.AP < 5) return;
            Stream.send('player_shoot', {'cid': cid});
        },
        heal: function(cid) {
            var data, aim;
            if (cid === undefined) {
                data = {};
                aim = this;
            } else {
                data = {'cid': cid};
                aim = app.characters[cid].model;
            }
            if (!this.healModeEnabled() || this.operationsBlocked ||
                aim.isDead() || aim.isFullHealth()  || this.AP < 4) return;

            Stream.send('player_heal', data);
        },
        stop: function() {
            Stream.send('player_stop');
        },
        destroy: function() {
            app.stage.removeChild(this.currentSprite);
            this.currentSprite.removeAllEventListeners();
        }

    });

});