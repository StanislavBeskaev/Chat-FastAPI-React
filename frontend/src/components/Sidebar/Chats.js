import React from 'react'
import {Button, ListGroup} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import messagesStore from '../../stores/messagesStore'
import {useSocket} from '../../contexts/SocketProvider'
import authStore from '../../stores/authStore'


const Chats = () => {
  const {sendStopTyping} = useSocket()
  const {chats, selectedChatId, selectedChatTyping} = messagesStore
  const {user} = authStore

  const changeChat = (chatId) => {
    if (selectedChatTyping) {
      sendStopTyping(selectedChatId)
    }

    messagesStore.setSelectedChatId(chatId)
  }


  return (
    <ListGroup variant="flush">
      {Object.keys(chats).map(chatId => {
        const isOwner = user.login === chats[chatId].creator
        const chatName = chats[chatId].chat_name
        return (
        <ListGroup.Item
          key={chatId}
          action
          onClick={() => changeChat(chatId)}
          active={selectedChatId === chatId}
        >
          <div className="d-flex justify-content-between">
            {chatName}
            {
              isOwner
                ? <Button
                  variant="success"
                  size="sm"
                  onClick={e => {
                    e.stopPropagation()
                    alert(`Тут будет изменение чата ${chatName}`)
                  }
                  }
                >Изменить</Button>
                : null
            }
          </div>
        </ListGroup.Item>)
      })}
    </ListGroup>
  )
}

export default observer(Chats)
