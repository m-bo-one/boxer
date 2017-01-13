this.app = this.app || {};

var Stream = function(app) {
    this.app = app;
};

Stream.send = function(msgType, data) {
    var jData = JSON.stringify({
        'msg_type': msgType,
        'data': data
    });
    app.ws.send(jData);
};
Stream.init = function() {
    var ws = new WebSocket("ws://" + window.location.hostname + ':9999' + "/game");
    _.extend(ws, Backbone.Events);

    ws.onopen = function(evt) {
        $('#conn_status').html('<b>WS Connected</b>');

        Stream.send('register_user',
                    {'uid': localStorage.getItem('uid'),
                     'token': localStorage.getItem('token')})

        ws.onmessage = function(evt) {
            var answer = JSON.parse(evt.data);
            var parsedData = answer.data;
            ws.trigger(answer.msg_type, parsedData);
        };
        ws.on('register_user', function(data) {
            app.user = new app.UserModel(data);
            // TODO: Maybe revert back to model??
            app.sprites[app.user.id] = new app.SpriteView({ model: app.user });

            app.hud = new app.HudView({ model: app.user });
            app.weaponVision = new app.WeaponVisionView({ model: app.user });
        });
        ws.on('users_map', function(data) {
            if (app.hud) app.hud.trigger('updateOnline', data.count);

            for (var j = 0; j < data.users.update.length; j++) {
                var charId = data.users.update[j].id;
                var updateData = data.users.update[j];

                if (app.users.hasOwnProperty(charId)) {
                    app.users[charId].refreshData(updateData);
                } else {
                    app.users[charId] = new app.UserModel(updateData);
                    app.sprites[charId] = new app.SpriteView({ model: app.users[charId] });  
                }
            }
            for (var i = 0; i < data.users.remove.length; i++) {
                var removeId = data.users.remove[i];
                if (app.users.hasOwnProperty(removeId)) {
                    app.sprites[removeId].destroy();
                    app.users[removeId].destroy();
                    if (app.user.id === removeId) {
                        app.weaponVision.destroy();
                        app.user.destroy();
                    }
                }
            }
        });
    };
    ws.onerror = function(evt) {
        $('#conn_status').html('<b>WS Error</b>');
    };
    ws.onclose = function(evt) {
        $('#conn_status').html('<b>WS Closed</b>');
    };
    app.ws = ws;
};
