function displayHideForm (element)  {
    const replyForm = $(element).find('> .individual-reply')
    if (replyForm.css('display') == "none" ) {
        replyForm.css('display','block');
    } else {
        replyForm.css('display','none');
    }
}
