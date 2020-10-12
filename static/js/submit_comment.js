function submitComment(event,form) {
    event.preventDefault();
    var $form = form;
    var data = $form.data();
    commentContent = $form.find("textarea.comment_form").val();
    $form.find("textarea.comment_form").val("")
    $.ajax({
        type: 'POST',
        url: '../new_comment/',
        data: {
            parentType: data.parentType,
            parentId: data.parentId,
            commentContent: commentContent,
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
            console.log('succccc')
            $(document).scrollTop($(document).height()); 
            if (data.parentType === 'post'){
                $('#main_comment_list').append(response.new_comment_html)
                
            } else {
                console.log('--------------------')
                console.log(response.new_comment_html)
                let selector_string = `.child_comments[comment_id=${data.parentId}]`
                $(selector_string).append(response.new_comment_html)
                displayHideForm($(form).parent().parent().parent())
            }
        }
    })
}
$('#main_form').on('submit',function(e){
    submitComment(e,$(this))
})

$(document).on('submit','.reply_form',function(e){
    submitComment(e,$(this))
})
