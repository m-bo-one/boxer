var app = app || {};


$(function() {
    $.get('/api/constants', function(data) {
        app.constants = data.data;
    });
});