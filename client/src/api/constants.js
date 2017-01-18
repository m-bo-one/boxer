require(['app', 'jquery'], function(app, $) {
    $.get('/api/constants', function(data) {
        app.constants = data.data;
    });
});