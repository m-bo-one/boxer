$(function() {
    var canvas = document.getElementById("myCanvas"),
        ctx = canvas.getContext("2d");

    window.keys = {};
    window.users = {};
    window.user = null;
    window.stage = new createjs.Stage(canvas);
    window.ws = new WebSocket("ws://" + window.location.hostname + ":" + 9999 + "/");
    window.addEventListener("keydown", function (e) {
        keys[e.keyCode] = true;
    });
    window.addEventListener("keyup", function (e) {
        keys[e.keyCode] = false;
    });

    // createjs.Ticker.useRAF = true;
    // createjs.Ticker.timingMode = createjs.Ticker.RAF_SYNCHED;
    createjs.Ticker.setFPS(60);
    createjs.Ticker.addEventListener("tick", gameLoop);

    function createAnimatedSprite(data) {

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

    function UserModel(userData) {
        this.id = userData.id;
        this.speed = userData.speed;
        this.username = userData.username;

        this.action = userData.action;
        this.direction = userData.direction;
        this.sprite = createAnimatedSprite(userData);

        users[this.id] = this;
    }
    UserModel.prototype.update = function(userData) {
        this.sprite.x = userData.x;
        this.sprite.y = userData.y;

        var way = getWay(userData.action, userData.direction);
        if (this.sprite.currentAnimation != way) {
            this.action = userData.action;
            this.direction = userData.direction;
            this.sprite.gotoAndPlay(way);
        }
    };
    UserModel.prototype.move = function(action, direction) {
        var data = JSON.stringify({
            msg_type: 'player_move',
            data: {
                'id': this.id,
                'action': action,
                'direction': direction
            }
        })
        ws.send(data);
    };
    UserModel.prototype.stop = function() {
        this.move("wait", this.direction);
    };
    UserModel.prototype.drop = function() {
        stage.removeChild(this.sprite);
        delete this;
    };

    function gameLoop(event) {

        stage.update();
        console.log('Current FPS: ' + createjs.Ticker.getMeasuredFPS());

        if (user === null) return;

        if (keys[38] && keys[87] || keys[40] && keys[83] || keys[39] && keys[68] || keys[37] && keys[65]) return;

        if (keys[38] || keys[87]) {
            user.move('walk', 'top');
        }
        else if (keys[40] || keys[83]) {
            user.move('walk', 'bottom');
        }
        else if (keys[39] || keys[68]) {
            user.move('walk', 'right');
        }
        else if (keys[37] || keys[65]) {
            user.move('walk', 'left');
        }

        if (!keys[38] && !keys[87] && !keys[40] && !keys[83] && !keys[39] && !keys[68] && !keys[37] && !keys[65]) {
            user.stop();
        }
        
    }

    window.onbeforeunload = function() {
        var data = JSON.stringify({
            msg_type: 'unregister_user'
        })
        ws.send(data);
    };
    ws.onmessage = function(evt) {
        var answer = JSON.parse(evt.data);
        var userData = answer.data;
        switch (answer.msg_type) {
            case 'render_map':
                canvas.width = userData.width;
                canvas.height = userData.height;
                break;
            case 'register_user':
                user = new UserModel(userData);
                break;
            case 'unregister_user':
                users[userData.id].drop();
                break;
            case 'player_move':
                user.update(userData);
                break;
            case 'users_map':
                for (var user_id in userData) {
                    user_id = parseInt(user_id);
                    if (user.id !== user_id) {
                        if (users.hasOwnProperty(user_id)) {
                            // console.log("User ID: " + user_id + "; way: " + getWay(users[user_id].action, users[user_id].direction));
                            users[user_id].update(userData[user_id]);
                        } else {
                            users[user_id] = new UserModel(userData[user_id]);   
                        }
                    }
                }
                break;
        }
    };
    ws.onopen = function(evt) {
        $('#conn_status').html('<b>WS Connected</b>');
    };
    ws.onerror = function(evt) {
        $('#conn_status').html('<b>WS Error</b>');
    };
    ws.onclose = function(evt) {
        $('#conn_status').html('<b>WS Closed</b>');
    };
});