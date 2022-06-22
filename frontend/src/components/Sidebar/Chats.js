import React from 'react'
import {Image, ListGroup} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import white_pencil from "../../img/white_pencil.png"
import blue_pencil from "../../img/blue_pencil.png"


import messagesStore from '../../stores/messagesStore'
import {useSocket} from '../../contexts/SocketProvider'
import authStore from '../../stores/authStore'
import changeChatNameModalStore from '../../stores/modals/changeChatNameModalStore'


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
            {
              isOwner
                ? <Image
                    src={selected ? white_pencil : blue_pencil}
                    height={20}
                    onMouseEnter={e => e.target.height = 23}
                    onMouseLeave={e => e.target.height = 20}
                    onClick={e => {
                      e.stopPropagation()
                      changeChatNameModalStore.openWithChatId(chatId)
                    }}
                  />
                : null
            }
          </div>
        </ListGroup.Item>)
      })}
    </ListGroup>
  )
}

export default observer(Chats)
