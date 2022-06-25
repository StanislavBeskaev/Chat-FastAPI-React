import React from 'react'
import {observer} from 'mobx-react-lite'
import {Modal, Alert} from 'react-bootstrap'

import chatMembersModalStore from '../../../stores/modals/chatMembersModalStore'
import messagesStore from '../../../stores/messagesStore'
import ChatMembers from './ChatMembers'
import ContactsOutsideChat from './ContactsOutsideChat'


const ChatMembersModal = () => {
  const {chatId, message} = chatMembersModalStore

  return (
    <>
      <Modal.Header closeButton>Участники чата "{messagesStore.getChatNameById(chatId)}"</Modal.Header>
      <Modal.Body className="pb-4">
        <div className="d-flex flex-column flex-grow-1 gap-3">
          <ChatMembers />
          <ContactsOutsideChat />
          {
            message
              ? <Alert variant="info" className="mt-3">{message}</Alert>
              : null
          }
        </div>
      </Modal.Body>
    </>
  )
}

export default observer(ChatMembersModal)