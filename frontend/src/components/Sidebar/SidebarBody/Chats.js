import React from 'react'
import {useHistory} from 'react-router-dom'
import {ListGroup, Badge} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import messagesStore from '../../../stores/messagesStore'
import socketStore from '../../../stores/socketStore'


const Chats = () => {
  const {chats, selectedChatId, selectedChatTyping} = messagesStore

  const history = useHistory()

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
      {messagesStore.getChatIds().map(chatId => {
        const chatName = chats[chatId].chat_name
        const selected = selectedChatId === chatId
        const notViewedMessagesCount = messagesStore.getChatNotViewedMessagesCount(chatId)
        return (
          <ListGroup.Item
            key={chatId}
            action
            onClick={() => changeChat(chatId)}
            active={selected}
          >
            <div className="d-flex justify-content-between">
              {chatName}
              {
                notViewedMessagesCount > 0
                  ? <Badge
                    pill
                    bg={selected ? 'light' : 'primary'}
                    className={`align-self-center ${selected ? 'text-primary' : ''}`}
                  >
                    {notViewedMessagesCount}
                  </Badge>
                  : null
              }
            </div>
          </ListGroup.Item>
        )
      })
      }
    </ListGroup>
  )
}

export default observer(Chats)
