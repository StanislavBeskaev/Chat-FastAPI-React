import React from 'react'
import {ListGroup, Badge} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import messagesStore from '../../../stores/messagesStore'
import {useSocket} from '../../../contexts/SocketProvider'
import {useHistory} from 'react-router-dom'


const Chats = () => {
  const {sendStopTyping, sendReadMessage} = useSocket()
  const {chats, selectedChatId, selectedChatTyping} = messagesStore

  const history = useHistory()

  const changeChat = (chatId) => {
    if (selectedChatTyping) {
      sendStopTyping(selectedChatId)
    }

    if (history.location.pathname !== '/') {
      history.push('/')
    }

    if (selectedChatId === chatId) return

    messagesStore.readAllMessagesInWaitList(sendReadMessage)
    messagesStore.setSelectedChatId(chatId)
  }

  return (
    <ListGroup variant="flush">
      {Object.keys(chats).map(chatId => {
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
                    bg={selected ? "light" : "primary"}
                    className={`align-self-center ${selected ? 'text-primary': ''}`}
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
