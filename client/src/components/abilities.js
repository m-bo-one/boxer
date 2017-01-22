define(['app', 'jquery', 'backbone', 'easel'], function(app, $, Backbone) {

    var Skill = function() {
        this.stage = app.stage;
        this._lastX = -25;
        this.initCoords = {
            x: this._lastX,
            y: -100,
            width: 50,
            height: 50
        };
        this.container = new createjs.Container().set({
            x: app.canvas.width / 2,
            y: app.canvas.height
        });
        this.stage.addChild(this.container);
    };

    Skill.prototype.add = function(skillInfo) {
        var childsCount = this.container.children.length;
        if (childsCount > 0) {
            this.initCoords.x = this._lastX - (childsCount * 3 * this.initCoords.width / 4);
            console.log(this.initCoords.x)
        }
        for (var i = 0; i < childsCount; i++) {
            var shape = this.container.children[i];
            this._drawRect(shape);
            this.initCoords.x += 3 * this.initCoords.width / 2;
        }
        var shape = this._drawRect();
        this.container.addChild(shape);
    };

    Skill.prototype._drawRect = function(shape) {
        var shape = shape || new createjs.Shape();
        var g = shape.graphics;
        g.clear();
        g.setStrokeStyle(0.5);
        g.beginStroke("#A9A9A9");
        g.drawRoundRect(
            this.initCoords.x,
            this.initCoords.y,
            this.initCoords.width,
            this.initCoords.height,
            3);
        return shape;
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
        skill.add();
        skill.add();
        // skill.add();
        skill.add();
        return skill;
    };

    return {
        Skill: Skill
    };

});