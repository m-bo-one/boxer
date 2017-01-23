define([
    'app',
    'jquery',
    'backbone',
    'easel'
], function(app, $, Backbone) {

    var SkillDescription = function(skill, image, info) {
        this.info = info;
        this.stage = app.stage;
        this.container = new createjs.Container().set({
            x: skill.container.x,
            y: skill.container.y,
            alpha: 0
        });

        this.width = 150;
        this.height = 200;
        this.y = -290;
        this.x = image.parent.x - 0.5 * (this.width - skill.initCoords.width);

        this.xIndent = 5;
        this.yIndent = 5;

        this.plotInfo();

        this.stage.addChild(this.container);
    };
    
    SkillDescription.prototype = {
        show: function() {
            this.container.alpha = 1;
        },
        hide: function() {
            this.container.alpha = 0;
        },
        remove: function() {
            this.stage.removeChild(this.container);
        },
        plotInfo: function() {
            this._plotBoundary();
            this._plotHeader(this.info.header || 'EMPTY');
            this._plotTypeEffect(this.info.typeEffects || []);
            this._plotDescription(this.info.description || 'Some empty description with big text and more more more more more empty descr.');
            this._plotCooldown(this.info.cooldown || 3);
            this._plotAPConsumption(this.info.AP || 5);
        },
        _plotBoundary: function() {
            var shape = new createjs.Shape().set({
                alpha: 0.75
            });

            shape.graphics
                .clear()
                .setStrokeStyle(1)
                .beginStroke("black")
                .beginFill("#2e3033")
                .drawRoundRect(this.x, this.y, this.width, this.height, 3)
                .endStroke();
            shape.cache(this.x, this.y, this.width, this.height);

            var tric = new createjs.Shape().set({
                alpha: 0.75,
                x: this.x + 0.5 * this.width,
                y: this.y + this.height
            });
            tric._diffX = 10;
            tric._diffY = 10;

            tric.graphics
                .clear()
                .setStrokeStyle(0.5)
                .beginStroke("black")
                .beginFill("#2e3033")
                .moveTo(0, tric._diffY)
                .lineTo(tric._diffX, 0)
                .lineTo(-tric._diffX, 0)
                .lineTo(0, tric._diffY)
                .endStroke();
            tric.cache(-tric._diffX, 0, tric._diffX * 2, tric._diffY);

            this.container.addChild(shape, tric);
        },
        _plotHeader: function(title) {
            var fontSize = 12;
            var text = new createjs.Text().set({
                x: this.x + this.xIndent,
                y: this.y + this.yIndent,
                lineWidth: this.width - this.xIndent,
                text: title,
                font: fontSize + 'px Arial',
                color: 'white'
            });
            var h = text.getMeasuredHeight();
            text.cache(0, 0, this.width - this.xIndent, h + fontSize);
            this.yIndent += this.xIndent + h;
            this.container.addChild(text);

            this._plotLine(text);
        },
        _plotLine: function(text, indent) {
            var indent = indent || 2,
                w = text.getMeasuredWidth(),
                h = text.getMeasuredHeight(),
                underline = new createjs.Shape();
            underline.graphics
                .s("white")
                .mt(text.x, text.y + h + indent + this.xIndent)
                .lt(text.x + w, text.y + h + indent + this.xIndent)
                .es();
            underline.cache(text.x, text.y + h + indent + this.xIndent, w, indent)
            this.yIndent += this.xIndent;
            this.container.addChild(underline);
        },
        _plotTypeEffect: function(effects) {
            var fontSize = 12;
            for (var i = 0; i < effects.length; i++) {
                var text = new createjs.Text().set({
                    x: this.x + this.xIndent,
                    y: this.y + this.yIndent,
                    lineWidth: this.width - this.xIndent,
                    text: effects[i].type + ': ' + effects[i].description,
                    font: fontSize + 'px Arial',
                    color: 'white'
                });
                text.cache(0, 0, this.width - this.xIndent, fontSize);
                this.yIndent += this.xIndent + fontSize;
                this.container.addChild(text);
            }

            this._plotLine(text);
        },
        _plotDescription: function(description) {
            var fontSize = 12;
            var text = new createjs.Text().set({
                x: this.x + this.xIndent,
                y: this.y + this.yIndent,
                lineWidth: this.width - this.xIndent,
                text: description,
                font: fontSize + 'px Arial',
                color: 'white'
            });
            var h = text.getMeasuredHeight();
            text.cache(0, 0, this.width - this.xIndent, h + fontSize);
            this.yIndent += this.xIndent + h;
            this.container.addChild(text);
        },
        _plotCooldown: function(time) {
            var fontSize = 12, custIndent = 5;
            var text1 = new createjs.Text().set({
                x: this.x + 5 * this.xIndent,
                y: this.y + this.yIndent + custIndent,
                lineWidth: this.width - this.xIndent,
                text: 'TIME: ',
                font: fontSize + 'px Arial',
                color: '#07ff14'
            });
            var w1 = text1.getMeasuredWidth();
            var text2 = new createjs.Text().set({
                x: this.x + 5 * this.xIndent + w1,
                y: this.y + this.yIndent + custIndent,
                lineWidth: this.width - this.xIndent,
                text: time,
                font: fontSize + 'px Arial',
                color: 'white'
            });
            var h1 = text1.getMeasuredHeight();
            var h2 = text2.getMeasuredHeight();
            text1.cache(0, 0, this.width - this.xIndent, h1 + fontSize);
            text2.cache(0, 0, this.width - this.xIndent, h2 + fontSize);
            this.yIndent += this.xIndent + h2;
            this.container.addChild(text1);
            this.container.addChild(text2);
        },
        _plotAPConsumption: function(APCount) {
            var fontSize = 12, custIndent = 10;
            var text1 = new createjs.Text().set({
                x: this.x + 5 * this.xIndent,
                y: this.y + this.yIndent + custIndent,
                lineWidth: this.width - this.xIndent,
                text: 'AP: ',
                font: fontSize + 'px Arial',
                color: '#07ff14'
            });
            var w1 = text1.getMeasuredWidth();
            var text2 = new createjs.Text().set({
                x: this.x + 5 * this.xIndent + w1,
                y: this.y + this.yIndent + custIndent,
                lineWidth: this.width - this.xIndent,
                text: APCount,
                font: fontSize + 'px Arial',
                color: 'white'
            });
            var h1 = text1.getMeasuredHeight();
            var h2 = text2.getMeasuredHeight();
            text1.cache(0, 0, this.width - this.xIndent, h1 + fontSize);
            text2.cache(0, 0, this.width - this.xIndent, h2 + fontSize);
            this.yIndent += this.xIndent + h2;
            this.container.addChild(text1);
            this.container.addChild(text2);
        }
    };
    SkillDescription.constructor = SkillDescription;

    var Skill = function() {
        this.canvas = app.canvas;
        this.stage = app.stage;
        this._lastX = -20;
        this.initCoords = {
            x: this._lastX,
            y: -75,
            width: 40,
            height: 40,
            scale: 1
        };
        this.container = new createjs.Container().set({
            x: app.canvas.width / 2,
            y: app.canvas.height
        });
        this.stage.addChild(this.container);
    };

    Skill.prototype.add = function(skillInfo) {
        var image, imageCont,
            childsCount = this.container.children.length;

        if (childsCount > 0) {
            this.initCoords.x = this._lastX - (this.initCoords.scale * childsCount * 3 * this.initCoords.width / 4);
        }

        for (var i = 0; i < childsCount; i++) {
            imageCont = this.container.children[i];
            imageCont.x = this.initCoords.x;
            imageCont.y = this.initCoords.y;

            this.initCoords.x += 3 * this.initCoords.width * this.initCoords.scale / 2;
        }

        this._createAbilityBox(skillInfo);
    };

    Skill.prototype._createAbilityBox = function(skillInfo) {
        var imageCont = new createjs.Container();
        imageCont.x = this.initCoords.x;
        imageCont.y = this.initCoords.y;

        var image = this.__createAbilityImg(skillInfo.image);
        var imgText = this.__createAbilityButton(skillInfo.button);

        imageCont.addChild(image, imgText);

        this.__regKey(skillInfo, image);

        this.container.addChild(imageCont);
    };

    Skill.prototype.__createAbilityImg = function(image) {
        var image = image.clone();
        image.scaleX = image.scaleY = this.initCoords.scale;
        return image;
    };

    Skill.prototype.__createAbilityButton = function(button) {
        var imgText = new createjs.Text();
        imgText.text = button.toUpperCase();
        imgText.x = 4;
        imgText.color = 'white';
        imgText.font = '30 px Russo One';
        imgText.scaleX = imgText.scaleY = this.initCoords.scale;
        return imgText;
    };

    Skill.prototype.__regKey = function(skillInfo, image) {
        var self = this;
        var buttonKey = skillInfo.button;
        var text = skillInfo.text;

        var _press = function(evt) {
            image.filters = [
                new createjs.ColorMatrixFilter(new createjs.ColorMatrix().adjustBrightness(-25))
            ];
            image.cache(0, 0, self.initCoords.width, self.initCoords.height);
            setTimeout(function() {
                image.uncache();
            }, 125);
            return false;
        };
        window.addEventListener("keydown", function(evt) {
            if (evt.key == buttonKey) {
                return _press(evt);
            }
        });
        image.on('click', _press);
        image.on('mouseover', function(evt) {

            if (!image.hasOwnProperty('skillDescription')) {
                image.skillDescription = new SkillDescription(self, image, text);
            }
            image.skillDescription.show();

            image.on('mouseout', function(evt) {
                image.skillDescription.hide();
            });
        });
    };

    Skill.prototype.remove = function(shape) {
        this.container.removeChild(shape);
    };

    Skill.prototype.clear = function() {
        this.stage.removeChild(this.container);
    };

    Skill.create = function(character) {
        var skill = new Skill();
        // TODO: Add skills in future;
        skill.add({
            image: app.baseImages['spell-runner'],
            button: 'q',
            text: {
                header: 'FIRST ABILITY',
                typeEffects: [
                    {type: 'ABILITY', description: 'Units'},
                    {type: 'AFFECTS', description: 'Creeps'},
                ]
            }
        });
        skill.add({
            image: app.baseImages['spell-invision'],
            button: 'w',
            text: {
                header: 'SECOND ABILITY',
                typeEffects: [
                    {type: 'ABILITY', description: 'Units'},
                    {type: 'AFFECTS', description: 'Creeps'},
                ]
            }
        });
        skill.add({
            image: app.baseImages['spell-headbones'],
            button: 'e',
            text: {
                header: 'THIRD ABILITY',
                typeEffects: [
                    {type: 'ABILITY', description: 'Units'},
                    {type: 'AFFECTS', description: 'Creeps'},
                ]
            }
        });
        skill.add({
            image: app.baseImages['spell-headbones'],
            button: 'r',
            text: {
                header: 'FOURTH ABILITY',
                typeEffects: [
                    {type: 'ABILITY', description: 'Units'},
                    {type: 'AFFECTS', description: 'Creeps'},
                ]
            }
        });
        // skill.add();
        // skill.add();
        // skill.add();
        return skill;
    };

    return {
        Skill: Skill
    };

});