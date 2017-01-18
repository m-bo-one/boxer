requirejs.config({
    baseUrl: "src/components/",
    paths: {
        domReady: 'domReady/domReady',
        jquery: 'jquery/dist/jquery.min',
        backbone: 'backbone/backbone-min',
        underscore: 'underscore/underscore-min',

        easel: 'EaselJS/lib/easeljs-0.8.2.min',
        tween: 'TweenJS/lib/tweenjs-0.6.2.min',
        sound: 'SoundJS/lib/soundjs-0.6.2.min',
        preload: 'PreloadJS/lib/preloadjs-0.6.2.min',

        utils: '../utils',
        app: '../app',
        stream: '../stream',
        preloader: '../preloader',
        appApi: '../api',
        appModels: '../models',
        appViews: '../views',
    },
    shim: {
        underscore: {
            exports: '_'
        },      
        backbone: {
            deps: ['underscore', 'jquery'],
            exports: 'Backbone'
        },
        easel: {
            exports: 'createjs'
        },
        tween: {
            deps: ['easel'],
            exports: 'Tween'
        },
        sound: {
            deps: ['easel'],
            exports: 'Sound'
        },
        preload: {
            deps: ['easel'],
            exports: 'Preload'
        }
    }
});
requirejs([
    'utils',
    'app',
    'preloader',
    'stream',
    'appApi/constants',
    'appApi/login',
    'appModels/users',
    'appViews/map',
    'appViews/hud',
    'appViews/sprites',
]);