window.onload = function() {
    var canvas = document.getElementById("myCanvas"),
        ctx = canvas.getContext("2d");

    window.keys = {};
    window.users = {};
    window.user = null;

    function sprite(options) {
                    
        var that = {};
                        
        that.context = options.context;
        that.x = options.x;
        that.y = options.y;
        that.width = options.width;
        that.height = options.height;
        that.image = options.image;
        that.label = options.label;

        that.render = function () {

            that.context.textAlign = "center"; 
            that.context.fillText(
                that.label,
                (2 * that.x + that.width) / 2,
                that.y - 2
            );
            that.context.drawImage(
               that.image,
               that.x,
               that.y,
               that.width,
               that.height);
        };

        return that;
    }

    function UserModel(userData) {
        this.id = userData.id;
        this.speed = userData.speed;
        this.username = userData.username;

        baseImage = new Image();
        baseImage.src = userData.image_url;

        this.sprite = sprite({
            context: ctx,
            x: userData.x,
            y: userData.y,
            label: userData.username,
            width: userData.width,
            height: userData.height,
            image: baseImage
        });


        this.direction;
        
        users[this.id] = this;
    }
    UserModel.prototype.redraw = function() {
        ctx.beginPath();
        this.sprite.render();
        ctx.fill();
    };
    UserModel.prototype.update = function(userData) {
        this.sprite.x = userData.x;
        this.sprite.y = userData.y;
    };
    UserModel.prototype.move = function(direction) {
        this.direction = direction;

        var data = JSON.stringify({
            msg_type: 'player_move',
            data: {
                'id': this.id,
                'direction': direction
            }
        })
        ws.send(data);
    };

    function gameLoop() {

        requestAnimationFrame(gameLoop);

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        for (var user_id in users) {
            users[user_id].redraw();
        }

        if (user === null) return;

        if (keys[38] || keys[87]) {
            user.move('top');
        }
        if (keys[40] || keys[83]) {
            user.move('bottom');
        }
        if (keys[39] || keys[68]) {
            user.move('right');
        }
        if (keys[37] || keys[65]) {
            user.move('left');
        }
        
    }

    gameLoop();

    document.body.addEventListener("keydown", function (e) {
        keys[e.keyCode] = true;
    });
    document.body.addEventListener("keyup", function (e) {
        keys[e.keyCode] = false;
    });

    // Open up a connection to our server
    var ws = new WebSocket("ws://" + window.location.hostname + ":" + 9999 + "/");

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
};