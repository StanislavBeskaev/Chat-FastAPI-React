import React from 'react'
import {observer} from 'mobx-react-lite'
import {Modal} from 'react-bootstrap'

import authStore from '../../stores/authStore'
import addContactModalStore from '../../stores/modals/addContactModalStore'
import changeChatNameModalStore from '../../stores/modals/changeChatNameModalStore'
import chatMembersModalStore from '../../stores/modals/chatMembersModalStore'
import confirmDeleteModalStore from '../../stores/modals/confirmDeleteModalStore'
import messagesStore from '../../stores/messagesStore'
import messageContextMenuStore from '../../stores/messageContextMenuStore'
import socketStore from '../../stores/socketStore'


import AddContactModal from '../Modals/AddContactModal'
import ChangeChatNameModal from '../Modals/ChangeChatNameModal'
import ChatMembersModal from '../Modals/ChatMembersModal/ChatMembersModal'
import ConfirmDeleteModal from '../Modals/ConfirmDeleteModal'
import MessageEditModal from '../Modals/MessageEditModal'

import ChatHeader from './ChatHeader'
import Loader from '../UI/Loader/Loader'
import Messages from './Messages/Messages'
import MessageContextMenu from './MessageContextMenu/MessageContextMenu'
import ScrollButton from './Messages/ScrollButton'
import TextForm from './TextForm'
import TypingInfo from './TypingInfo'



function SimpleChat() {

  const {loading, selectedChatId, isLoadMessages, loadError} = messagesStore
  const {login} = authStore.user

  const sendTextMessage = (text) => {
    socketStore.sendText(text, selectedChatId)
  }

  const closeAddContactModal = () => {
    addContactModalStore.close()
  }

  if (loadError) {
    return <h2 className="m-5 text-danger">Возникла ошибка при загрузке сообщений</h2>
  }

  if (loading || !isLoadMessages) {
    return <Loader />
  }

  return (
    <div style={{maxWidth: '75%'}} className="d-flex flex-column flex-grow-1">
      <ChatHeader />
      <div className="flex-grow-1 overflow-auto">
        <div className="d-flex flex-column align-items-start justify-content-end px-3">
          <Messages messages={messagesStore.selectedChatMessages()} login={login}/>
          <ScrollButton />
        </div>
      </div>
      <div className="mt-2">
        <TypingInfo logins={messagesStore.selectedChatTypingLogins()}/>
      </div>
      <TextForm
        sendTextMessage={sendTextMessage}
        sendStartTyping={() => socketStore.sendStartTyping(selectedChatId)}
        sendStopTyping={() => socketStore.sendStopTyping(selectedChatId)}
      />
      <MessageContextMenu />
      <Modal
        show={addContactModalStore.show}
        onHide={closeAddContactModal}
      >
        <AddContactModal />
      </Modal>
      <Modal
        show={changeChatNameModalStore.show}
        onHide={() => changeChatNameModalStore.close()}
      >
        <ChangeChatNameModal />
      </Modal>
      <Modal
        show={chatMembersModalStore.show}
        onHide={() => chatMembersModalStore.close()}
      >
        <ChatMembersModal />
      </Modal>
      <Modal
        show={messageContextMenuStore.showMessageEditModal}
        onHide={() => messageContextMenuStore.closeMessageEditModal()}
      >
        <MessageEditModal />
      </Modal>
      <Modal
        show={confirmDeleteModalStore.show}
        onHide={() => confirmDeleteModalStore.close()}
      >
        <ConfirmDeleteModal />
      </Modal>
    </div>
  )
}

export default observer(SimpleChat)