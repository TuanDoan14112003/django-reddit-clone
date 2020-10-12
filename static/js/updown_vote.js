function vote(voteButton) {
    console.log('send')
    var $voteDiv = $(voteButton).parent().parent();
    var $data = $voteDiv.data();
    var direction_name = $(voteButton).attr('title');
    var vote_value = null;
    if (direction_name == "upvote") {
        vote_value = 1;
    } else if (direction_name == "downvote") {
        vote_value = -1;
    } else {
        return;
    }
    $.ajax({
        type: 'POST',
        url: '/vote/',
        data: {
            what: $data.whatType,
            what_id: $data.whatId,
            vote_value: vote_value,
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
                    if (response.error == null) {
            var voteDiff = response.voteDiff;
            var $score = null;
            var $upvoteArrow = null;
            var $downArrow = null;
            if ($data.whatType == 'post') {
                $score = $voteDiv.find("p.score");
                $upvoteArrow = $voteDiv.children("div").children('i.fas.fa-arrow-alt-circle-up');
                $downArrow = $voteDiv.children("div").children('i.fas.fa-arrow-alt-circle-down');
            } 
            else if ($data.whatType == 'comment') {
                console.log($voteDiv)
                $score = $voteDiv.siblings('.comment-details').children('.score')
                $upvoteArrow = $voteDiv.find('i.fa-arrow-alt-circle-up');
                $downArrow = $voteDiv.find('i.fa-arrow-alt-circle-down');
            }

            // update vote elements

            if (vote_value == -1) {
                if ($upvoteArrow.hasClass("voted")) { // remove upvote, if any.
                    $upvoteArrow.removeClass("voted")
                }
                if ($downArrow.hasClass("voted")) { // Canceled downvote
                    $downArrow.removeClass("voted")
                } else {                                // new downvote
                    $downArrow.addClass("voted")
                }
            } else if (vote_value == 1) {               // remove downvote
                if ($downArrow.hasClass("voted")) {
                    $downArrow.removeClass("voted")
                }

                if ($upvoteArrow.hasClass("voted")) { // if canceling upvote
                    $upvoteArrow.removeClass("voted")
                } else {                                // adding new upvote
                    $upvoteArrow.addClass("voted")
                }
            }

            // update score element
            var scoreInt = parseInt($score.text());
            var new_value = scoreInt + voteDiff
            console.log(scoreInt)
            if ($data.whatType === 'comment'){
                $score.text(new_value + ' points');
            } else {
                $score.text(new_value);
            }
        }
        }
    })

}
