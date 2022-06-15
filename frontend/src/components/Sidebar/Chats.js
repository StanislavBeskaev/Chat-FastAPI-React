import React from 'react'
import { ListGroup } from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import messagesStore from '../../stores/messagesStore'
import {useSocket} from '../../contexts/SocketProvider'


const Chats = () => {
  const {sendStopTyping} = useSocket()
  const {chats, selectedChatId, selectedChatTyping} = messagesStore

  const changeChat = (chatId) => {
    if (selectedChatTyping) {
      sendStopTyping(selectedChatId)
    }

    messagesStore.setSelectedChatId(chatId)
  }


  return (
    <ListGroup variant="flush">
      {Object.keys(chats).map(chatId => (
        <ListGroup.Item
          key={chatId}
          action
          onClick={() => changeChat(chatId)}
          active={selectedChatId === chatId}
        >
          {chats[chatId].chat_name}
        </ListGroup.Item>
      ))}
    </ListGroup>
  )
}

export default observer(Chats)
