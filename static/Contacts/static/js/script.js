$('document').ready(function () {
    /* validation */
    $("#register-form").validate({
        rules:
            {
                user_name: {
                    required: true,
                    minlength: 3
                },
                password: {
                    required: true,
                    minlength: 8,
                    maxlength: 15
                },
                cpassword: {
                    required: true,
                    equalTo: '#password'
                },
                user_email: {
                    required: true,
                    email: true
                },
            },
        messages:
            {
                user_name: "Enter a Valid Username",
                password: {
                    required: "Provide a Password",
                    minlength: "Password Needs To Be Minimum of 8 Characters"
                },
                user_email: "Enter a Valid Email",
                cpassword: {
                    required: "Retype Your Password",
                    equalTo: "Password Mismatch! Retype"
                }
            },
        submitHandler: submitForm
    });
    /* validation */

    /* form submit */
    function submitForm() {
        var data = $("#register-form").serialize();

        $.ajax({
                type: 'POST',
                url: '/api/v1/contacts/' + data.namespace,
                data: data,
                beforeSend: function () {
                    $("#error").fadeOut();
                    $("#btn-submit").html('<span class="glyphicon glyphicon-transfer"></span> &nbsp; 发送 ...');
                },
                success: function (data) {
                    if (data.code == 200) {
                        $("#btn-submit").html('Signing Up');
                        setTimeout('$(".form-signin").fadeOut(500, function(){ $(".signin-form").load("/api/v1/contacts/"+data.data); }); ', 5000);
                    }
                    else if (data.code == 400) {
                        $("#error").fadeIn(1000, function () {
                            $("#error").html('<div class="alert alert-danger"> <span class="glyphicon' +
                                ' glyphicon-info-sign"></span> &nbsp; 请联系danceiny@gmail.com。</div>');

                            $("#btn-submit").html('<span class="glyphicon glyphicon-log-in"></span> &nbsp; Create Account');

                        });
                    }

                }
            }
        );
        return false;
    }

    /* form submit */

})
;