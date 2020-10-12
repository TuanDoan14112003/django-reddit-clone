$('#notification_box').on('click',function(){
    console.log('vao day roi')
    $('.number-of-notification').text('0')
    $.ajax({
        type: 'POST',
        url: '/read-all-notification/',
        data: {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
            console.log('clear all notification')
        }
    })
})
// like and comment notification
let likeCommentNotificationSocket = new ReconnectingWebSocket(
    'ws://' + window.location.host +
    '/ws/like-comment-notification/');


function fetchNotifications() {
    likeCommentNotificationSocket.send(JSON.stringify({'command': 'fetch_like_comment_notifications'}));
}

function createLikeCommentNotification(notification) {
    console.log(notification)
    let single = `<a class="dropdown-item d-flex align-items-between" href="/post/${notification.post}">
    <div class="noti-image">
        <img src="${notification.profile.image}" alt="">
    </div>
    <div class="noti-content">
        <p class="noti-conntent-top"> <span>u/${notification.actor.username} </span>${notification.verb}</p>
        <p class="noti-conntent-bot">just now</p>
    </div>
  </a>`;
    $('#notification_list').prepend(single);


}

likeCommentNotificationSocket.onopen = function (e) {
    fetchNotifications();
};

likeCommentNotificationSocket.onmessage = function (event) {
    let data = JSON.parse(event.data);
    if (data['command'] === 'notifications') {
        let notifications = JSON.parse(data['notifications']);
        $('.number-of-notification').text(notifications.length);
        for (let i = 0; i < notifications.length; i++) {
            createLikeCommentNotification(notifications[i]);
        }
    } else if (data['command'] === 'new_like_comment_notification') {
        let notification = $('.number-of-notification');
        notification.text(parseInt(notification.text()) + 1);
        createLikeCommentNotification(JSON.parse(data['notification']));
    }
};

// $('#mark-like-comment-notifications-as-read').click(function () {

//     let url = $(this).data('url');

//     $.ajaxSetup({
//         headers: {
//             'X-CSRFToken': csrfmiddlewaretoken
//         }
//     });

//     $.ajax({
//         type: 'POST',
//         url: url,
//         dataType: 'json',
//         success: function (res) {
//             console.log(res);
//             if (res.status === false) {
//             }
//             if (res.status === true) {}

//         },
//         error: function (err) {
//             console.log(err);
//         }
//     });
// });
