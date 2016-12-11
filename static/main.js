$(function() {
    var canvas = document.getElementById("myCanvas"),
        ctx = canvas.getContext("2d");

    canvas.width = 300;
    canvas.height = 300;
    window.keys = {};
    window.users = {};
    window.user = null;
        //user = new UserModel(x=20, y=20, width=20, height=20, speed=2);
        
    function getRandomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    function update(obj/*, …*/) {
        for (var i=1; i<arguments.length; i++) {
            for (var prop in arguments[i]) {
                var val = arguments[i][prop];
                if (typeof val == "object") // this also applies to arrays or null!
                    update(obj[prop], val);
                else
                    obj[prop] = val;
            }
        }
        return obj;
    }

    function UserModel(id, x, y, width, height, speed, friction) {
        this.id = id;
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.speed = speed;
        this.friction = friction;
        this.direction;
        
        users[id] = this;
    }
    UserModel.prototype.collide = function(other) {
      if (this !== other && this.x < other.x + other.width &&
         this.x + this.width > other.x &&
         this.y < other.y + other.height &&
         this.height + this.y > other.y) {
          return true;
      } else {
          return false;
      }
    };
    UserModel.prototype.redraw = function() {
        ctx.beginPath();
        ctx.fillRect(this.x, this.y, this.width, this.height);
        ctx.fill();
    };
    UserModel.prototype.clear = function() {
        ctx.clearRect(this.x, this.y, this.width, this.height);
    };
    UserModel.prototype.update = function(x, y) {
        this.x = x;
        this.y = y;
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
        // console.log('Direction: ' + this.direction);
        // console.log('UID: ' + this.id);
        ws.send(data);
    };

    function update() {

        requestAnimationFrame(update);

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

    update();

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
                user = new UserModel(userData.id,
                                     userData.x,
                                     userData.y,
                                     userData.width,
                                     userData.height,
                                     userData.speed,
                                     userData.friction);
                break;
            case 'unregister_user':
                delete users[userData.id];
                break;
            case 'player_move':
                user = users[userData.id];
                user.update(userData.x,
                            userData.y);
                break;
            case 'users_map':
                for (var user_id in userData) {
                    user_id = parseInt(user_id);
                    if (user.id !== user_id) {
                        if (users.hasOwnProperty(user_id)) {
                            users[user_id].update(userData[user_id].x,
                                                  userData[user_id].y);
                        } else {
                            users[user_id] = new UserModel(userData[user_id].id,
                                                           userData[user_id].x,
                                                           userData[user_id].y,
                                                           userData[user_id].width,
                                                           userData[user_id].height,
                                                           userData[user_id].speed,
                                                           userData[user_id].friction);   
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