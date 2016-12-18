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
            sprites: null
        },
        initialize: function(options) {
            this.id = options.id;
            this.speed = options.speed;
            this.username = options.username;
            this.action = options.action;
            this.direction = options.direction;
            this.currentArmor = options.current_armor;
            this.currentWeapon = options.current_weapon;

            this.loadSprites(options);

            app.users[this.id] = this;
        },
        loadSprites: function(options) {
            this._sprites = {}
            for (var compoundKey in options.sprites) {
                this._sprites[compoundKey] = createAnimatedSprite(options, compoundKey);
            }
            this.switchToSprite(options.current_sprite);
            app.stage.addChild(this.currentSprite);
        },
        switchToSprite: function(compoundKey) {
            this._currentSpriteKey = compoundKey;
            this.currentSprite = this._sprites[compoundKey];
        },
        equipWeapon: function(weaponName) {
            var weaponName = weaponName || this.currentWeapon;
            var data = JSON.stringify({
                msg_type: 'player_equip',
                data: {'equipment': 'weapon'}
            })
            app.ws.send(data);
            this._weaponEquiped = true;
        },
        update: function(options) {
            this.currentSprite.x = options.x;
            this.currentSprite.y = options.y;
            this.action = options.action;
            this.direction = options.direction;

            var way = getWay(options.action, options.direction);
            if (this.currentSprite.currentAnimation != way) {
                this.currentSprite.gotoAndPlay(way);
            }
            if (this._currentSpriteKey != options.current_sprite) {
                this.currentSprite.stop();
                app.stage.removeChild(this.currentSprite);
                this.switchToSprite(options.current_sprite);
                this.currentSprite.x = options.x;
                this.currentSprite.y = options.y;
                app.stage.addChild(this.currentSprite);
                this.currentSprite.gotoAndPlay(way);
            }
        },
        move: function(action, direction) {
            var data = JSON.stringify({
                msg_type: 'player_move',
                data: {
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
            app.stage.removeChild(this.currentSprite);
            delete this;
        }
    });
})();