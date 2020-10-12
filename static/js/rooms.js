$(function () {
  let chatClient;
  let currentChannel;
  let currentChannelSid;
  let currentChannelDiv;
  let username;
  $('.conversation').on('click', async function () {
    currentChannelSid = $(this).attr('sid')
    currentChannel = await chatClient.getChannelBySid(currentChannelSid)
    currentChannelDiv = $(`[sid=${currentChannelSid}]`)
    console.log(currentChannelDiv.attr('conversation_title'))
    $('.conversation-title').text(currentChannelDiv.attr('conversation_title'))
    $('.list-messages').html('')
    queryMessages(currentChannel)
  })

  function addMessage(message) {
    const messageWrapper = document.createElement('div')
    messageWrapper.classList.add('message', 'infinite-item')
    if (message.author === username) {
      messageWrapper.classList.add('mine')
      messageWrapper.innerHTML = `
      <div class="content">${message.body}</div>
      `
    } else {
      messageWrapper.classList.add('their')
      messageWrapper.innerHTML = `
      <div class="content">${message.body}</div>
      `
    }
    document.querySelector('.list-messages')
      .appendChild(messageWrapper)
  }

  function queryMessages(channel) {
    channel.getMessages().then(async function (messages) {
      for (message of messages.items) {
        addMessage(message)
      }
      if (messages.hasPrevPage) {
        preMessages = await messages.prevPage()
        console.log(preMessages)
      }
    })
  }
  
  $.getJSON(
    "/token", {
      device: "browser"
    },
    function (data) {
      Twilio.Chat.Client.create(data.token).then(async function (client) {
        // Use client
        chatClient = client;
        username = data.identity
        room_list = await chatClient.getSubscribedChannels()
        console.log(room_list)
        // default channel
        currentChannel = room_list.items[0]
        currentChannelSid = currentChannel['sid']
        currentChannelDiv = $(`[sid=${currentChannelSid}]`)
        $('.conversation-title').text(currentChannelDiv.attr('conversation_title'))
        queryMessages(currentChannel)
        for (channel of room_list.items) {
          channel.getMessages(1).then(async function (message) {
            newest_message = message.items[0]
            $(`[sid=${newest_message.channel.sid}] > .new-message`).text(newest_message.body)
          })
          channel.on("messageAdded", function (message) {
            $(`[sid=${message.channel.sid}] > .new-message`).text(message.body)

            if (message.channel.sid === currentChannelSid) {
              addMessage(message)
            }
          })
        };
      });
      let $form = $("#send-message-form");
      let $input = $("#message-input");

      $form.on("submit", function (e) {
        e.preventDefault();
        if (currentChannel && $input.val().trim().length > 0) {
          currentChannel.sendMessage($input.val());
          $input.val("");
        }
      });

    })
})