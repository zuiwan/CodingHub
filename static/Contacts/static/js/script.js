$('document').ready(function () {
    /* validation */
    $("#register-form").validate({
        rules:
            {
                name: {
                    required: true
                },
                password: {
                    required: true,
                    minlength: 6,
                    maxlength: 15
                },
                cpassword: {
                    required: true,
                    equalTo: '#password'
                },
                email: {
                    required: false,
                    email: true
                },
                phone: {
                    required: true,
                    minlength: 11
                },
                city: {
                    required: true
                }
            },
        messages:
            {
                password: {
                    required: "Provide a Password",
                    minlength: "Password Needs To Be Minimum of 6 Characters"
                },
                email: "Enter a Valid Email",
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
        console.log(data);
        $.ajax({
                type: 'POST',
                url: '/api/v1/contacts/' + $("#namespace").val(),
                data: data,
                beforeSend: function () {
                    $("#error").fadeOut();
                    $("#btn-submit").html('<span class="glyphicon glyphicon-transfer"></span> &nbsp; 发送 ...');
                },
                success: function (data) {
                    if (data.code == 200) {
                        $("#btn-submit").html('Signing Up');
                        $("#error").html('<div class="alert alert-danger"> <span class="glyphicon' +
                            ' glyphicon-info-sign"></span> &nbsp; 注册成功。如有问题，可联系微信：tanceiny。</div>');
                        // setTimeout('$(".form-signin").fadeOut(500, function(){$(".signin-form").load(_url); }); ', 1000);
                        function Redirect() {
                            window.location = "https://api.cannot.cc/ContactsView/" + data.data;
                        }
                        setTimeout('Redirect()', 1000);
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