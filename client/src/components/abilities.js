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

        var image = this.__createAbilityImg(skillInfo.button, skillInfo.description, skillInfo.image);
        var imgText = this.__createAbilityButton(skillInfo.button);

        imageCont.addChild(image, imgText);

        this.container.addChild(imageCont);
    };

    Skill.prototype.__createAbilityImg = function(button, description, image) {
        var image = image.clone();
        image.scaleX = image.scaleY = this.initCoords.scale;

        this.__regKey(button, description, image);
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

    Skill.prototype.__regKey = function(buttonKey, description, image) {
        var self = this;
        var description = description || 'Empty description';
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
        image.on('mouseover', function(evt, description) {
            var _cont = new createjs.Container();
            _cont.x = self.container.x;
            _cont.y = self.container.y;

            var width = 150, height = 200, y = -290,
                x = image.parent.x - 0.5 * (width - self.initCoords.width);

            var shape = new createjs.Shape().set({
                alpha: 0.75
            });

            shape.graphics
                .clear()
                .setStrokeStyle(0.5)
                .beginStroke("black")
                .beginFill("#2e3033")
                .drawRoundRect(x, y, width, height, 3)
                .endStroke();

            _cont.addChild(shape);

            var tric = new createjs.Shape().set({
                alpha: 0.75,
                x: x + 0.5 * width,
                y: y + height
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

            _cont.addChild(tric);

            var text = new createjs.Text().set({
                x: x,
                y: y,
                lineWidth: width,
                text: description,
                font: '12px Russo One'
            });
            _cont.addChild(text);

            self.stage.addChild(_cont);

            image.on('mouseout', function(evt) {
                self.stage.removeChild(_cont);
            });
        }, null, false, description);
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
            description: "Fewfewfwefwef wefwefwef wefwefwe"
        });
        skill.add({
            image: app.baseImages['spell-invision'],
            button: 'w'
        });
        skill.add({
            image: app.baseImages['spell-headbones'],
            button: 'e'
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