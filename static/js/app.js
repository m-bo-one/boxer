var app = app || {};

$(function () {
  'use strict';

  var gameLoop = function(event) {
    /** Keys notation
    * 49 - '1'
    * 38 - 'w'
    * 40 - 's'
    * 39 - 'd'
    * 37 - 'a'
    * 87 - key up
    * 83 - key down
    * 68 - key right
    * 65 - key left
    **/

    app.stage.update();
    app._LOG('Current FPS: ' + createjs.Ticker.getMeasuredFPS());

    if (app.user === null || app.keys[38] && app.keys[87] || app.keys[40] && app.keys[83] ||
      app.keys[39] && app.keys[68] || app.keys[37] && app.keys[65]) return;

    if (app.keys[38] || app.keys[87]) {
      app.user.move('walk', 'top');
    }
    else if (app.keys[40] || app.keys[83]) {
      app.user.move('walk', 'bottom');
    }
    else if (app.keys[39] || app.keys[68]) {
      app.user.move('walk', 'right');
    }
    else if (app.keys[37] || app.keys[65]) {
      app.user.move('walk', 'left');
    }
      
  };

  var Socket = {
    ws: null,

    init: function () {
      var ws = new WebSocket("ws://" + window.location.hostname + ":" + 9999 + "/game");

      ws.onmessage = function(evt) {
        var answer = JSON.parse(evt.data);
        var parsedData = answer.data;
        switch (answer.msg_type) {
          case 'render_map':
            app.canvas.width = parsedData.width;
            app.canvas.height = parsedData.height;
            break;
          case 'register_user':
            app.user = new app.UserModel(parsedData);
            break;
          case 'unregister_user':
            app.users[parsedData.id].destroy();
            break;
          case 'player_update':
            app.user.refreshData(parsedData);
            break;
          case 'users_map':
            for (var user_id in parsedData) {
              user_id = parseInt(user_id);
              if (app.user && app.user.id !== user_id) {
                if (app.users.hasOwnProperty(user_id)) {
                  app.users[user_id].refreshData(parsedData[user_id]);
                } else {
                  app.users[user_id] = new app.UserModel(parsedData[user_id]);   
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

      this.ws = ws;
    }
  };


  app.canvas = document.getElementById("gameBoard"),
  app.ctx = app.canvas.getContext("2d");
  app.keys = {};
  app.users = {};
  app.user = null;
  app.stage = new createjs.Stage(app.canvas);
  app.DEBUG = false;
  app._LOG = function(data) {
    if (this.DEBUG) console.log(data);
  };

  Socket.init();
  app.ws = Socket.ws;

  createjs.Ticker.setFPS(60);
  createjs.Ticker.addEventListener("tick", gameLoop);

  window.addEventListener("keydown", function (e) {
    app.keys[e.keyCode] = true;
    // button '1'
    if (app.keys[49]) {
      app.user.equipWeapon();
    }
  });
  window.addEventListener("keyup", function (e) {
    app.keys[e.keyCode] = false;

    if (app.user && !app.keys[38] && !app.keys[87] && !app.keys[40] &&
        !app.keys[83] && !app.keys[39] && !app.keys[68] && !app.keys[37] &&
        !app.keys[65]) app.user.stop();
  });
  window.onbeforeunload = function() {
    var data = JSON.stringify({
      msg_type: 'unregister_user'
    })
    app.ws.send(data);
  };

  // Backbone.sync = function(method, model, options) {
  //   options || (options = {});

  //   switch (method) {
  //     case 'create':
  //       break;

  //     case 'update':
  //       setTimeout(function() {
  //         app.ws.send(JSON.stringify(model.changed));
  //       }, 0);
  //       break;

  //     case 'delete':
  //       break;

  //     case 'read':
  //       break;
  //   }
  // };
});