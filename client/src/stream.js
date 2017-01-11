this.app = this.app || {};

var Stream = function(app) {
    this.app = app;
};

Stream.prototype = {

    send: function(msgType, data) {
        var jData = JSON.stringify({
            'msg_type': msgType,
            'data': data
        });
        this.app.ws.send(jData);
    }
};
Stream.prototype.constructor = Stream;
Stream.init = function() {
    var ws = new WebSocket("ws://" + window.location.hostname + ':9999' + "/game");
    _.extend(ws, Backbone.Events);

    ws.onmessage = function(evt) {
        var answer = JSON.parse(evt.data);
        var parsedData = answer.data;
        ws.trigger(answer.msg_type, parsedData);
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
    ws.on('register_user', function(data) {
        app.user = new app.UserModel(data);
        // TODO: Maybe revert back to model??
        app.sprites[app.user.id] = new app.SpriteView({ model: app.user });

        app.hud = new app.HudView({ model: app.user });
        app.weaponVision = new app.WeaponVisionView({ model: app.user });
    });
    ws.on('users_map', function(data) {
        if (app.hud) app.hud.trigger('updateOnline', data.count);

        for (var user_id in data.users.update) {
            user_id = parseInt(user_id, 0);

            var updateData = data.users.update[user_id];
            updateData = (typeof updateData === 'string') ? JSON.parse(updateData) : updateData;
            if (app.users.hasOwnProperty(user_id)) {
                app.users[user_id].refreshData(updateData);
            } else {
                app.users[user_id] = new app.UserModel(updateData);
                app.sprites[user_id] = new app.SpriteView({ model: app.users[user_id] });  
            }
        }
        for (var i = 0; i < data.users.remove.length; i++) {
            var removeId = data.users.remove[0];
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

    this.app.ws = ws;
};
