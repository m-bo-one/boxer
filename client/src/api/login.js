var app = app || {};


(function() {
    window.onload = function() {
        $('#quickLogin').on('submit', function(e) {
            e.preventDefault();

            $('.login-error').empty();

            var url = e.currentTarget.action;
            var method = e.currentTarget.method;
            var data = {
                'username': $(this).find('input#username').val(),
                'password': $(this).find('input#password').val()
            }

            $.ajax({
                method: method,
                url: url,
                data: JSON.stringify(data),
                contentType : 'application/json'
            }).done(function(data) {
                $('.login-error').css('color', 'green');
                $('.login-error').html(data.message);
                localStorage.setItem("uid", data.data.uid);
                localStorage.setItem("token", data.data.token);
                Stream.init(app);
                console.log(data);
            }).fail(function(response) {
                var data = JSON.parse(response.responseText);
                $('.login-error').css('color', 'red');
                $('.login-error').html(data.message);
                console.log(data);
            });
        });
    };
})();