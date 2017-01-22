define([
    'app',
    'appViews/HudView',
    'backbone',
    'underscore'
], function(app, HudView, Backbone, _) {

    var Stream = function(app) {};

    Stream.send = function(msgType, data) {
        var jData = JSON.stringify({
            'msg_type': msgType,
            'data': data
        });
        app.ws.send(jData);
    };
    Stream.init = function() {
        var ws = new WebSocket("ws://" + app.config.WS.HOST + ':' + app.config.WS.PORT + "/game");
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
                app.characters[data.id] = {};
                app.characters[data.id]['model'] = new app.CharacterModel(data);

                app.currentCharacter = app.characters[data.id];
                // TODO: Maybe revert back to model??
                app.characters[data.id]['sprite'] = new app.SpriteView({
                    model: app.currentCharacter.model
                });

                app.characters[data.id]['hud'] = new HudView({app: app});
            });
            ws.on('users_map', function(data) {
                if (app.currentCharacter) {
                    app.currentCharacter.hud.trigger('updateOnline', data.count);
                }

                for (var j = 0; j < data.users.update.length; j++) {
                    var charId = data.users.update[j].id;
                    var updateData = data.users.update[j];

                    if (app.characters.hasOwnProperty(charId)) {
                        app.characters[charId]['model'].refreshData(updateData);
                    } else {
                        app.characters[charId] = {};
                        app.characters[charId]['model'] = new app.CharacterModel(updateData);
                        app.characters[charId]['sprite'] = new app.SpriteView({
                            model: app.characters[charId]['model']
                        });  
                    }
                }
                for (var i = 0; i < data.users.remove.length; i++) {
                    var removeId = data.users.remove[i];
                    if (app.characters.hasOwnProperty(removeId)) {
                        for (var key in app.characters[removeId]) {
                            app.characters[removeId][key].destroy();
                        }
                        delete app.characters[removeId];
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

        window.onbeforeunload = function() {
            Stream.send('unregister_user');
        };

        app.ws = ws;
    };

    return Stream;
});