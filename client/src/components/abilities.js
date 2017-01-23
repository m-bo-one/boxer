define(['app', 'jquery', 'backbone', 'easel'], function(app, $, Backbone) {

    var Skill = function() {
        this.canvas = app.canvas;
        this.stage = app.stage;
        this._lastX = -20;
        // this.keys = {
        //     q: 81,
        //     w: 87,
        //     e: 69,
        //     r: 82
        // }
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
        var imageCont,
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

        var image = this.__createAbilityImg(skillInfo.button, skillInfo.image);
        var imgText = this.__createAbilityButton(skillInfo.button);
        // var descr = this.__createAbilityDescription(skillInfo.description);

        imageCont.addChild(imgText, image);

        this.container.addChild(imageCont);
    };

    // Skill.prototype.__createAbilityDescription = function(description) {
    //     var shape = new createjs.Shape();

    //     shape.x = this.initCoords.x;
    //     shape.y = this.initCoords.y;

    //     shape.graphics
    //         .clear()
    //         .setStrokeStyle(0.5)
    //         .beginStroke("black")
    //         .beginFill("grey")
    //         .drawRect(0, 0, 100, 100)
    //         .endStroke();

    //     return shape;
    // };

    Skill.prototype.__createAbilityImg = function(button, image) {
        var image = image.clone();
        image.scaleX = image.scaleY = this.initCoords.scale;

        this.__regKey(button, image);
        return image;
    };

    Skill.prototype.__createAbilityButton = function(button) {
        var imgText = new createjs.Text();
        imgText.text = button;
        imgText.x = 4;
        imgText.color = 'white';
        imgText.font = '30 px Russo One';
        imgText.scaleX = imgText.scaleY = this.initCoords.scale;
        return imgText;
    };

    Skill.prototype.__regKey = function(buttonKey, image) {
        var self = this;

        window.addEventListener("keydown", function(evt) {
            if (evt.key == buttonKey) {
                return _press(evt);
            }
        });
        image.on('click', function(evt) {
            image.filters = [
                new createjs.ColorMatrixFilter(new createjs.ColorMatrix().adjustBrightness(-25))
            ];
            image.cache(0, 0, self.initCoords.width, self.initCoords.height);
            setTimeout(function() {
                image.uncache();
            }, 125);
            return false;
        });
        image.on('mouseover', function(evt) {
            var shape = new createjs.Shape().set({
                x: self.container.x,
                y: self.container.y,
            });

            shape.graphics
                .clear()
                .setStrokeStyle(0.5)
                .beginStroke("black")
                .beginFill("grey")
                .drawRect(
                    self._lastX - (self.initCoords.scale * childsCount * 3 * self.initCoords.width / 4);,
                    self.initCoords.y, 100, 100)
                .endStroke();

            self.stage.addChild(shape);

            image.on('mouseout', function(evt) {
                self.stage.removeChild(shape);
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
        skill.add({image: app.baseImages['spell-runner'], button: 'q'});
        skill.add({image: app.baseImages['spell-invision'], button: 'w'});
        skill.add({image: app.baseImages['spell-headbones'], button: 'e'});
        // skill.add();
        // skill.add();
        // skill.add();
        return skill;
    };

    return {
        Skill: Skill
    };

});