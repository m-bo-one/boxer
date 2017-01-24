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
        this.consumerColors = {
            'AP': '#07ff14',
            'HP': 'red'
        };

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
            this._plotCooldown(this.info.cooldown || null);
            if (this.info.consumer) {
                this._plotPointConsumption(this.info.consumer.type || null,
                                           this.info.consumer.value || null);
            }
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
                .endFill()
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
                .lt(text.x + this.width - 2 * this.xIndent, text.y + h + indent + this.xIndent)
                .es();
            underline.cache(text.x, text.y + h + indent + this.xIndent, this.width - 2 * this.xIndent, indent)
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
            if (time === null) return;
            var fontSize = 12, custIndent = 5;
            var image1 = app.baseImages['clock'].clone();
            image1.x = this.x + this.xIndent;
            image1.y = this.y + this.yIndent + custIndent;

            image1.scaleX = image1.scaleY = 0.8;

            var w1 = image1.getBounds().width;
            var text2 = new createjs.Text().set({
                x: this.x + this.xIndent + w1 + 4,
                y: this.y + this.yIndent + custIndent,
                lineWidth: this.width - this.xIndent,
                text: time,
                font: fontSize + 'px Arial',
                color: 'white'
            });
            var h1 = image1.getBounds().height;
            var h2 = text2.getMeasuredHeight();
            image1.cache(0, 0, w1, h1);
            text2.cache(0, 0, this.width - this.xIndent, h2 + fontSize);
            this.yIndent += this.xIndent + h2;
            this.container.addChild(image1, text2);
        },
        _plotPointConsumption: function(type, value) {
            if (type === null || value === null) return;
            var fontSize = 12, custIndent = 10;
            var text1 = new createjs.Text().set({
                x: this.x + this.xIndent,
                y: this.y + this.yIndent + custIndent,
                lineWidth: this.width - this.xIndent,
                text: type + ': ',
                font: fontSize + 'px Arial',
                color: this.consumerColors[type] || 'white'
            });
            var w1 = text1.getMeasuredWidth();
            var text2 = new createjs.Text().set({
                x: this.x + this.xIndent + w1,
                y: this.y + this.yIndent + custIndent,
                lineWidth: this.width - this.xIndent,
                text: value,
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

    /** Skill constructor */
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
    /**
     * @param {object} skillInfo [Object with skill block info]
     */
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
    /** @param {object} [Object with skill block info]  */
    Skill.prototype._createAbilityBox = function(skillInfo) {
        var imageCont = new createjs.Container();
        imageCont.x = this.initCoords.x;
        imageCont.y = this.initCoords.y;

        var image = this.__createAbilityImg(skillInfo.imageName);
        imageCont.addChild(image);

        var cooldown = skillInfo.cooldown || 0;
        if (cooldown > 0) {
            var imgText = this.__createAbilityButton(skillInfo.button);
            imageCont.addChild(imgText);

            var cooldownBox = this.__createCooldownBox(skillInfo.cooldown);
            imageCont.addChild(cooldownBox);
        } else {
            image.filters = [
                new createjs.ColorMatrixFilter(new createjs.ColorMatrix().adjustBrightness(-25))
            ];
            image.cache(0, 0, this.initCoords.width, this.initCoords.height);
        }
        this.__regKey(skillInfo, image);

        this.container.addChild(imageCont);
    };

    /**
     * [__createAbilityImg description]
     * @param  {string} imageName [Image name of ability]
     * @return {object}           [Bitmap instance]
     */
    Skill.prototype.__createAbilityImg = function(imageName) {
        var image = app.baseImages[imageName].clone();
        image.scaleX = image.scaleY = this.initCoords.scale;
        return image;
    };

    Skill.prototype.__createCooldownBox = function(cooldown) {
        var cont = new createjs.Container().set({alpha: 0.7});
        var box = new createjs.Shape();
        box.scaleX = box.scaleY = this.initCoords.scale;

        box.graphics
            .clear()
            .setStrokeStyle(0.5)
            .beginStroke("black")
            .beginFill("black")
            .drawRoundRect(0, 0, this.initCoords.width, this.initCoords.height, 3)
            .endFill()
            .endStroke();

        cont.addChild(box);

        var fontSize = 20;
        var text = new createjs.Text().set({
            text: cooldown,
            font: fontSize + 'px Arial',
            color: 'white'
        });
        var w = text.getMeasuredWidth();
        var h = text.getMeasuredHeight();
        text.x = 0.5 * (this.initCoords.width - w);
        text.y = 0.5 * (this.initCoords.height - h);
        cont.addChild(text);
        return cont;
    };

    Skill.prototype.__createAbilityButton = function(button) {
        var imgText = new createjs.Text();
        imgText.text = button.toUpperCase();
        imgText.x = 4;
        imgText.y = 2;
        imgText.color = 'white';
        imgText.font = '40 px Russo One';
        imgText.scaleX = imgText.scaleY = this.initCoords.scale;
        return imgText;
    };

    Skill.prototype.__regKey = function(skillInfo, image) {
        var self = this;
        var buttonKey = skillInfo.button;
        var text = skillInfo.text;
        text.cooldown = skillInfo.cooldown || 0;

        if (text.cooldown > 0) {
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
        }
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

    Skill.prototype.remove = function() {
        var cont = this.container.children.pop();
        this.container.removeChild(cont);
    };

    Skill.prototype.clear = function() {
        this.stage.removeChild(this.container);
    };

    Skill.create = function(character) {
        var skill = new Skill();
        // TODO: Add skills in future;
        skill.add({
            imageName: 'spell-invision',
            button: 'q',
            cooldown: 5,
            text: {
                header: 'FIRST ABILITY',
                typeEffects: [
                    {type: 'ABILITY', description: 'Units'},
                    {type: 'AFFECTS', description: 'Creeps'},
                ],
                consumer: {
                    type: "AP",
                    value: 10
                }
            }
        });
        skill.add({
            imageName: 'spell-runner',
            button: 'w',
            // cooldown: 5,
            text: {
                header: 'SECOND ABILITY',
                typeEffects: [
                    {type: 'ABILITY', description: 'Units'},
                    {type: 'AFFECTS', description: 'Creeps'},
                ],
                consumer: {
                    type: "BONUS",
                    value: "Ability to run"
                }
            }
        });
        skill.add({
            imageName: 'spell-headbones',
            button: 'e',
            cooldown: 5,
            text: {
                header: 'THIRD ABILITY',
                typeEffects: [
                    {type: 'ABILITY', description: 'Units'},
                    {type: 'AFFECTS', description: 'Creeps'},
                ],
                consumer: {
                    type: "AP",
                    value: 10
                }
            }
        });
        skill.add({
            imageName: 'spell-night',
            button: 'r',
            // cooldown: 5,
            text: {
                header: 'FOURTH ABILITY',
                typeEffects: [
                    {type: 'ABILITY', description: 'Units'},
                    {type: 'AFFECTS', description: 'Creeps'},
                ],
                consumer: {
                    type: "DMG",
                    value: "+300%"
                }
            }
        });
        return skill;
    };

    return {
        Skill: Skill
    };

});