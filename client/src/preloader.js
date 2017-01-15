var app = app || {};

(function () {
    var queue, ss, s;

    app.baseSprites = {};
    app.baseImages = {};

    var onPreloadFile = function(evt) {
        switch (evt.item.type) {
            case createjs.AbstractLoader.SPRITESHEET:
                ss = evt.result;
                s = new createjs.Sprite(ss);

                /* simlink */
                s.width = ss._frameWidth;
                s.height = ss._frameHeight;

                app.baseSprites[evt.item.id] = s;
                break;
            case createjs.AbstractLoader.SOUND:
                break;
            case createjs.AbstractLoader.IMAGE:
                app.baseImages[evt.item.id] = new createjs.Bitmap(evt.result);
                break;
        }
    }

    var onPreloadComplete = function(evt) {
        createjs.Sound.muted = true;

        app.stage.addChildAt(app.baseImages['map'], 0);
        $(app.canvas).show();
        $('#conn_status').show();
        if (!app.config.is_authorized) {
            $('.login').show();
        }
        $('.cssload-preloader').hide();
        Stream.init(app);
    }

    queue = new createjs.LoadQueue(true);
    queue.setMaxConnections(20);
    queue.installPlugin(createjs.Sound);
    queue.on("fileload", onPreloadFile, this);
    queue.on("complete", onPreloadComplete, this);
    queue.loadManifest('assets/manifest.json');

})();