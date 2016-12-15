$(function() {
    var canvas = document.getElementById("myCanvas"),
        ctx = canvas.getContext("2d");

    window.keys = {};
    window.users = {};
    window.user = null;
    window.stage = new createjs.Stage(canvas);
    window.ws = new WebSocket("ws://" + window.location.hostname + ":" + 9999 + "/");

    createjs.Ticker.useRAF = true;
    createjs.Ticker.timingMode = createjs.Ticker.RAF_SYNCHED;
    createjs.Ticker.setFPS(60);
    createjs.Ticker.addEventListener("tick", gameLoop);

    function createAnimatedSprite(data, currentAction) {

        var sh = new createjs.SpriteSheet(data.sprite);
        character = new createjs.Sprite(sh);
        character.x = data.x;
        character.y = data.y;
        character.width = data.sprite.frames.width;
        character.height = data.sprite.frames.height;
        character.gotoAndStop(currentAction);
        stage.addChild(character);

        return character;
    }

    function UserModel(userData) {
        this.id = userData.id;
        this.speed = userData.speed;
        this.username = userData.username;

        this.action = "wait";
        this.sprite = createAnimatedSprite(userData, this.action);
        
        users[this.id] = this;
    }
    // UserModel.prototype.redraw = function() {
    //     ctx.beginPath();
    //     this.sprite.render();
    //     ctx.fill();
    // };
    UserModel.prototype.update = function(userData) {
        this.sprite.x = userData.x;
        this.sprite.y = userData.y;
    };
    UserModel.prototype.move = function(action) {
        if (this.sprite.currentAnimation != action) {
            this.action = action;
            this.sprite.gotoAndPlay(action);
        }

        var data = JSON.stringify({
            msg_type: 'player_move',
            data: {
                'id': this.id,
                'action': action
            }
        })
        ws.send(data);
    };
    UserModel.prototype.stop = function() {
        this.action = 'wait';
        this.sprite.gotoAndStop('wait');
    };

    function gameLoop(event) {

        // ctx.clearRect(0, 0, canvas.width, canvas.height);
        stage.update();

        // for (var user_id in users) {
        //     users[user_id].redraw();
        // }

        if (user === null) return;

        if (keys[38] && keys[87] || keys[40] && keys[83] || keys[39] && keys[68] || keys[37] && keys[65]) return;

        if (keys[38] || keys[87]) {
            user.move('walk_top');
        }
        else if (keys[40] || keys[83]) {
            user.move('walk_bottom');
        }
        else if (keys[39] || keys[68]) {
            user.move('walk_right');
        }
        else if (keys[37] || keys[65]) {
            user.move('walk_left');
        }

        if (!keys[38] && !keys[87] && !keys[40] && !keys[83] && !keys[39] && !keys[68] && !keys[37] && !keys[65]) {
            user.stop();
        }
        
    }

    window.addEventListener("keydown", function (e) {
        keys[e.keyCode] = true;
    });
    window.addEventListener("keyup", function (e) {
        keys[e.keyCode] = false;
    });

    window.onbeforeunload = function() {
        var data = JSON.stringify({
            msg_type: 'unregister_user'
        })
        ws.send(data);
    };

    // What do we do when we get a message?
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
                delete users[userData.id];
                break;
            case 'player_move':
                user = users[userData.id];
                user.update(userData);
                break;
            case 'users_map':
                for (var user_id in userData) {
                    user_id = parseInt(user_id);
                    if (user.id !== user_id) {
                        if (users.hasOwnProperty(user_id)) {
                            users[user_id].update(userData[user_id]);
                        } else {
                            users[user_id] = new UserModel(userData[user_id]);   
                        }
                    }
                }
                break;
        }
    }
    // Just update our conn_status field with the connection status
    ws.onopen = function(evt) {
        $('#conn_status').html('<b>WS Connected</b>');
        var data = JSON.stringify({msg_type: 'register_user'})
        ws.send(data);
    }
    ws.onerror = function(evt) {
        $('#conn_status').html('<b>WS Error</b>');
    }
    ws.onclose = function(evt) {
        $('#conn_status').html('<b>WS Closed</b>');
    }
});