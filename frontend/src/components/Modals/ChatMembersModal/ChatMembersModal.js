import React from 'react'
import {observer} from 'mobx-react-lite'
import {Modal} from 'react-bootstrap'

import chatMembersModalStore from '../../../stores/modals/chatMembersModalStore'
import messagesStore from '../../../stores/messagesStore'
import ChatMembers from './ChatMembers'
import ContactsOutsideChat from './ContactsOutsideChat'


const ChatMembersModal = () => {
  const {chatId} = chatMembersModalStore

  return (
    <>
      <Modal.Header closeButton>Участники чата "{messagesStore.getChatNameById(chatId)}"</Modal.Header>
      <Modal.Body className="pb-4">
        <div className="d-flex flex-column flex-grow-1 gap-3">
          <ChatMembers />
          <ContactsOutsideChat />
        </div>
      </Modal.Body>
    </>
  )
}

export default observer(ChatMembersModal)