$(function() {
    var passwordField = $('input[type="password"]');
    var showPasswordCheckbox = $('input[type="checkbox"]');
    showPasswordCheckbox.on('change', function() {
        if ($(this).is(':checked')) {
                passwordField.attr('type', 'text');
                } else {
                    passwordField.attr('type', 'password');
                        }
                });
});