requirejs.config({
    baseUrl: "src/lib/",
    paths: {
        domReady: 'domReady/domReady',
        jquery: 'jquery/dist/jquery.min',
        backbone: 'backbone/backbone-min',
        underscore: 'underscore/underscore-min',

        easel: 'EaselJS/lib/easeljs-0.8.2.min',
        tween: 'TweenJS/lib/tweenjs-0.6.2.min',
        sound: 'SoundJS/lib/soundjs-0.6.2.min',
        preload: 'PreloadJS/lib/preloadjs-0.6.2.min',

        config: '../config',
        utils: '../utils',
        app: '../app',
        stream: '../stream',
        preloader: '../preloader',
        appApi: '../api',
        appModels: '../models',
        appViews: '../views',
        components: '../components',
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
        },

        utils: {
            deps: ['config']
        },
        app: {
            deps: ['config']
        },
        stream: {
            deps: ['app']
        },
        preloader: {
            deps: ['app', 'stream']
        },
        appViews: {
            deps: ['components/abilities']
        }
    }
});
requirejs([
    'app',
    'preloader',
    'appApi/constants',
    'appApi/login',
    'appModels/characters',
    'appViews/map',
    'appViews/hud',
    'appViews/sprites',
]);