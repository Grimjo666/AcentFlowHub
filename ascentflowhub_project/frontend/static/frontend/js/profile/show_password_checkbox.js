document.addEventListener("DOMContentLoaded", function () {
    var showPassCheckbox = document.getElementById("show-pass-checkbox");
    var passwordInput = document.getElementById("id_password");
    var passwordRepeatInput = document.getElementById("id_password_repeat");

    showPassCheckbox.addEventListener("change", function () {
        if (showPassCheckbox.checked) {
            passwordInput.type = "text";
            passwordRepeatInput.type = "text";
        } else {
            passwordInput.type = "password";
            passwordRepeatInput.type = "password";
        }
    });
});
