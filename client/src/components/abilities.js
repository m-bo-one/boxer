define(['app', 'jquery', 'backbone', 'easel'], function(app, $, Backbone) {

    var Skill = function() {
        this.stage = app.stage;
        this._lastX = -20;
        this.initCoords = {
            x: this._lastX,
            y: -75,
            width: 40,
            height: 40,
            scale: 1.5
        };
        this.container = new createjs.Container().set({
            x: app.canvas.width / 2,
            y: app.canvas.height
        });
        this.stage.addChild(this.container);
    };

    Skill.prototype.add = function(skillInfo) {
        var image, imageCont, imgText;
        var childsCount = this.container.children.length;
        if (childsCount > 0) {
            this.initCoords.x = this._lastX - (this.initCoords.scale * childsCount * 3 * this.initCoords.width / 4);
        }
        for (var i = 0; i < childsCount; i++) {
            imageCont = this.container.children[i];
            imageCont.x = this.initCoords.x;
            imageCont.y = this.initCoords.y;

            var bounds = imageCont.getBounds();
            imageCont.cache(bounds.x, bounds.y, bounds.width, bounds.height);

            this.initCoords.x += 5 * this.initCoords.width * this.initCoords.scale / 4;
            console.log(this.initCoords.x);
        }
        imageCont = new createjs.Container();
        imageCont.x = this.initCoords.x;
        imageCont.y = this.initCoords.y;

        image = skillInfo.image.clone();
        image.scaleX = image.scaleY = this.initCoords.scale;
        // image.mask = this._drawRect();

        imgText = new createjs.Text();
        imgText.text = skillInfo.button;
        imgText.x = 4;
        imgText.color = 'white';
        imgText.font = '30 px Russo One';
        imgText.scaleX = imgText.scaleY = this.initCoords.scale;

        imageCont.addChild(imgText);
        imageCont.addChildAt(image, 0);

        var bounds = imageCont.getBounds();
        imageCont.cache(bounds.x, bounds.y, bounds.width, bounds.height);

        this.container.addChild(imageCont);
    };

    Skill.prototype._drawRect = function() {
        var graphics = new createjs.Graphics()
            .clear()
            .setStrokeStyle(1)
            .beginStroke("#A9A9A9")
            .drawRoundRect(
                this.initCoords.x,
                this.initCoords.y,
                this.initCoords.width,
                this.initCoords.height,
                3)

        return new createjs.Shape(graphics);
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