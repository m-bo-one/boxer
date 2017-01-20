define(['app', 'jquery', 'backbone', 'easel'], function(app, $, Backbone) {

    var Skill = function() {
        this.stage = app.stage;
        this.initCoords = {
            x: app.canvas.width / 2,
            y: app.canvas.height
        };
        this.container = new createjs.Container().set(this.initCoords);
        this.stage.addChild(this.container);
    };

    Skill.prototype.add = function(skillInfo) {
        var lastCoords, el;
        if (this.container.children.length === 0) {
            lastCoords = {
                x: -50,
                y: -100,
                width: 50,
                height: 50
            };
        } else {
            for (var i = 0; i < this.container.children.length; i++) {
                el = this.container.children[i];
                el.x = -el.x - (this.container.children.length * 4 / el.width);
                lastCoords = {
                    x: el.x - el.width / 4,
                    y: -100,
                    width: el.width,
                    height: el.height
                };                
            }
        }
        console.log(lastCoords);
        var traitShape = new createjs.Shape();
        var g = traitShape.graphics;
        g.setStrokeStyle(0.5);
        g.beginStroke("#A9A9A9");
        g.drawRoundRect(
            lastCoords.x,
            lastCoords.y,
            lastCoords.width,
            lastCoords.height,
            3);
        traitShape.width = lastCoords.width;
        traitShape.height = lastCoords.height;

        this.container.addChild(traitShape);

        window.qwe = traitShape;
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
        // skill.add();
        skill.add();
        return skill;
    };

    return {
        Skill: Skill
    };

});