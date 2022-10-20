import React from 'react'
import {useHistory} from 'react-router-dom'
import {ListGroup} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import messagesStore from '../../../stores/messagesStore'
import socketStore from '../../../stores/socketStore'
import Chat from "./Chat"


const Chats = () => {
  const {chats, selectedChatId, selectedChatTyping} = messagesStore

  const history = useHistory()
  const chatIds = messagesStore.getChatIds()

  const changeChat = (chatId) => {
    if (selectedChatTyping) {
      socketStore.sendStopTyping(selectedChatId)
    }

    if (history.location.pathname !== '/') {
      history.push('/')
    }

    if (selectedChatId === chatId) return

    messagesStore.readAllMessagesInWaitList()
    messagesStore.setSelectedChatId(chatId)
  }

  return (
    <ListGroup variant="flush">
      {chatIds.map(chatId => (
          <ListGroup.Item
            key={chatId}
            action
            onClick={() => changeChat(chatId)}
            active={selectedChatId === chatId}
          >
            <Chat
              chatId={chatId}
              chatName={chats[chatId].chat_name}
              selected={selectedChatId === chatId}
              notViewedMessagesCount={messagesStore.getChatNotViewedMessagesCount(chatId)}
            />
          </ListGroup.Item>
      ))}
    </ListGroup>
  )
}

export default observer(Chats)
