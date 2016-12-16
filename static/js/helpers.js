function createAnimatedSprite(stage, data) {

    var sh = new createjs.SpriteSheet(data.sprite);
    character = new createjs.Sprite(sh);
    character.x = data.x;
    character.y = data.y;
    character.width = data.sprite.frames.width;
    character.height = data.sprite.frames.height;
    character.gotoAndStop(getWay(data.action, data.direction));
    stage.addChild(character);

    return character;
}

function getWay(action, direction) {
    return action + "_" + direction;
}