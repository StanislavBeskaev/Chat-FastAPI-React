import React from 'react'
import {Image} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'


import messagesStore from '../../stores/messagesStore'
import authStore from '../../stores/authStore'
import changeChatNameModalStore from '../../stores/modals/changeChatNameModalStore'
import chatMembersModalStore from '../../stores/modals/chatMembersModalStore'

import white_pencil from '../../img/white_pencil.png'
import white_add_contact from '../../img/white_add_contact.png'


const ChatHeader = () => {
  const {selectedChatId} = messagesStore
  const {user} = authStore
  const isOwner = user.login === messagesStore.getSelectedChatCreator()

  return (
    <div className="p-2 ps-3 bg-primary text-white">
      <div className="d-flex justify-content-between align-items-center">
        <div className="fs-4">
          {messagesStore.getSelectedChatName()}
        </div>
        <div className="d-flex align-items-center" style={{gap: "0.75rem"}}>
          <Image
            src={white_add_contact}
            height={27}
            style={{cursor: "pointer"}}
            onMouseEnter={e => e.target.height = 30}
            onMouseLeave={e => e.target.height = 27}
            onClick={async () => {
              await chatMembersModalStore.openWithChatId(selectedChatId)
            }}
          />
          {
            isOwner
              ? <Image
                src={white_pencil}
                height={20}
                style={{cursor: "pointer"}}
                onMouseEnter={e => e.target.height = 23}
                onMouseLeave={e => e.target.height = 20}
                onClick={() => {
                  changeChatNameModalStore.openWithChatId(selectedChatId)
                }}
              />
              : null
          }
        </div>
      </div>
    </div>
  )
}

export default observer(ChatHeader)