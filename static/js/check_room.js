message_btn = $('#chat-btn')
u1 = message_btn.attr('u1')
u2 = message_btn.attr('u2')


message_btn.on('click', function (e) {
    $('#chat-btn').prop('disabled',true)
    $.ajax({
        method: 'POST',
        url: '/check-room/',
        data: {
            u1: u1,
            u2: u2,
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
        },
        success:function(){
            window.location.href = 'http://' + window.location.host + '/chat/'
        }
    })
})