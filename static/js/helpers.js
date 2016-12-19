function createAnimatedSprite(data, animKey) {

    var sh = new createjs.SpriteSheet(data.sprites[animKey]);
    character = new createjs.Sprite(sh);
    character.x = data.x;
    character.y = data.y;
    character.width = data.sprites[animKey].frames.width;
    character.height = data.sprites[animKey].frames.height;
    character.gotoAndPlay(getSpriteWay(data.action, data.direction));

    return character;
}

function getSpriteWay(action, direction) {
    return action + "_" + direction;
}
