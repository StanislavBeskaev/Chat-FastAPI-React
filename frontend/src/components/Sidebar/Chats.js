import React from 'react'
import { ListGroup } from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import messagesStore from '../../stores/messagesStore'


const Chats = () => {
  const {chats, selectedChatId} = messagesStore
  return (
    <ListGroup variant="flush">
      {Object.keys(chats).map(chatId => (
        <ListGroup.Item
          key={chatId}
          action
          onClick={() => messagesStore.setSelectedChatId(chatId)}  // TODO при переключении между чатами останавливать typing
          active={selectedChatId === chatId}
        >
          {chats[chatId].chat_name}
        </ListGroup.Item>
      ))}
    </ListGroup>
  )
}

export default observer(Chats)
