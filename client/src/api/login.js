require(['app', 'jquery', 'domReady!'], function(app, $, domReady) {

    $('#quickLogin').on('submit', function(e) {
        e.preventDefault();

        $('.login-error').empty();

        var url;
        var method = e.currentTarget.method;
        var data = {
            'username': $(this).find('input#username').val(),
            'password': $(this).find('input#password').val()
        }
        if ($(this).find('input[type="checkbox"]').is(':checked')) {
            url = '/api/login';
        } else {
            url = '/api/registration'
        }
        $.ajax({
            method: method,
            url: url,
            data: JSON.stringify(data),
            contentType : 'application/json'
        }).done(function(data) {
            $('.login').hide();
            // $('.login-error').css('color', 'green');
            // $('.login-error').html(data.message);
            // Stream.init(app);
            console.log(data);
        }).fail(function(response) {
            var data = JSON.parse(response.responseText);
            $('.login-error').css('color', 'red');
            $('.login-error').html(data.message);
            console.log(data);
        });
    });

});