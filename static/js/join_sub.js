$('#join_sub').on('click',function(e){
    $.ajax({
        method: 'POST',
        url: 'join_sub/',
        data: {
            'subreddit_id': $('#join_sub').attr('subreddit_id'),
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
        },
        success:function(response) {
            console.log('join thanh cong')
            $('#join_sub button').text('Joined')
            $('#join_sub button').attr('disabled', true)
        }
    })
})