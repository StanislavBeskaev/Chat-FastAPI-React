import React from 'react'
import {ListGroup} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import messagesStore from '../../../stores/messagesStore'
import {useSocket} from '../../../contexts/SocketProvider'
import {useHistory} from 'react-router-dom'


const Chats = () => {
  const {sendStopTyping} = useSocket()
  const {chats, selectedChatId, selectedChatTyping} = messagesStore

  const history = useHistory()

  const changeChat = (chatId) => {
    if (selectedChatTyping) {
      sendStopTyping(selectedChatId)
    }

    messagesStore.setSelectedChatId(chatId)

    if (history.location.pathname !== '/') {
      history.push('/')
    }
  }

  return (
    <ListGroup variant="flush">
      {Object.keys(chats).map(chatId => {
        const chatName = chats[chatId].chat_name
        const selected = selectedChatId === chatId
        return (
        <ListGroup.Item
          key={chatId}
          action
          onClick={() => changeChat(chatId)}
          active={selected}
        >
          <div className="d-flex justify-content-between">
            {chatName}
          </div>
        </ListGroup.Item>)
      })}
    </ListGroup>
  )
}

export default observer(Chats)