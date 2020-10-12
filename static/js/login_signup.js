// Day la backend
let signup_username_ok = false;
let signup_email_ok = false;
let signup_password1_ok = false;
let signup_password2_ok = false;
let signup_field_ok = false;
let login_username_ok = false;
let login_password_ok = false;
$('#login_form input').on('input',function(){
    let field = this.id.split('_')[1]
    login_field = '#'+'login_' + field
    login_field_error = login_field + '_error'
    if ($(this).val() === "") {
        if (field === 'username') {
            login_username_ok = false;
        } else {
            login_password_ok = false;
        }
        $(login_field_error).text("You must fill this field")
        $(login_field_error).siblings("input").removeClass('valid')
        $(login_field_error).siblings("input").addClass('invalid')
    } else {
        if (field === 'username') {
            login_username_ok = true;
        } else {
            login_password_ok = true;
        }
        $(login_field_error).text('')
        $(login_field_error).siblings("input").removeClass('invalid')
        $(login_field_error).siblings("input").addClass('valid')
    }
    if (login_username_ok && login_password_ok) {
        $('#login_submit').attr("disabled", false);
    } else {
        $('#login_submit').attr("disabled", true);
    }
})



$('#signup_form input').on('input',function(){
    let field = this.id.split('_')[1]
    signup_field = '#'+'signup_' + field
    signup_field_error = signup_field + '_error'


    if ($(signup_field).val() == "") {
        signup_field_ok = false;
        $(signup_field_error).text("You must fill this field")
        $(signup_field_error).siblings("input").removeClass('valid')
        $(signup_field_error).siblings("input").addClass('invalid')
    } else {
        signup_field_ok = true;
        if (field === 'username' || field === 'email') {
            validate_username_email(field)
        }
        else if (field === 'password1' || field === 'password2') {
            validate_passwords()
        }
    }

    if (signup_field_ok && signup_email_ok && signup_username_ok && signup_password1_ok && signup_password2_ok) {
        $('#register_submit').attr("disabled", false);
    }
    else {
        $('#register_submit').attr("disabled", true);
    }
})

function validate_username_email(field) { 
    if (field === 'username') {
        let $username_error = $('#signup_username_error')
        $.ajax({
            method: 'POST',
            url: '/register/',
            async : false,
            data: {
                field: 'username',
                username: $('#signup_username').val(),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.error !== 'success') {
                    
                    signup_username_ok = false;
                    $username_error.text(response.error)
                    $username_error.siblings("input").removeClass('valid')
                    $username_error.siblings("input").addClass('invalid')
                } else {
                    signup_username_ok = true;
                    $username_error.text('')
                    $username_error.siblings("input").removeClass('invalid')
                    $username_error.siblings("input").addClass('valid')
                }
            }
        })
    }
    else if (field === 'email') {
        let $email_error = $('#signup_email_error')
        $.ajax({
            method: 'POST',
            url: '/register/',
            async : false,
            data: {
                field: 'email',
                email: $('#signup_email').val(),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.error !== 'success') {
                    signup_email_ok = false;
                    $email_error.text(response.error)
                    $email_error.siblings("input").removeClass('valid')
                    $email_error.siblings("input").addClass('invalid')
                } else {
                    signup_email_ok = true;
                    $email_error.text('')
                    $email_error.siblings("input").removeClass('invalid')
                    $email_error.siblings("input").addClass('valid')
                }
            }
        })
    }

}

function validate_passwords() {
    let $password1 = $('#signup_password1').val()
    let $password2 = $('#signup_password2').val()
    let $password1_error = $('#signup_password1_error')
    let $password2_error = $('#signup_password2_error')
    if ($password1.length<8) {
        signup_password1_ok = false;
        $password1_error.text('Your password is too short')
        $password1_error.siblings("input").removeClass('valid')
        $password1_error.siblings("input").addClass('invalid')
    } else {
        signup_password1_ok = true;
        $password1_error.text('')
        $password1_error.siblings("input").removeClass('invalid')
        $password1_error.siblings("input").addClass('valid')
    }
    if ($password1 !== $password2) {
        signup_password2_ok = false;
        $password2_error.text("Passwords don't match")
        $password2_error.siblings("input").removeClass('valid')
        $password2_error.siblings("input").addClass('invalid')
    } else{
        signup_password2_ok = true;
        $password2_error.text("")
        $password2_error.siblings("input").removeClass('invalid')
        $password2_error.siblings("input").addClass('valid')
    }
}