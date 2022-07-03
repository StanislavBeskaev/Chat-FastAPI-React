import React from 'react'
import {observer} from 'mobx-react-lite'
import {Modal} from 'react-bootstrap'

import {useSocket} from '../../contexts/SocketProvider'

import authStore from '../../stores/authStore'
import addContactModalStore from '../../stores/modals/addContactModalStore'
import AddContactModal from '../Modals/AddContactModal'
import changeChatNameModalStore from '../../stores/modals/changeChatNameModalStore'
import ChangeChatNameModal from '../Modals/ChangeChatNameModal'
import messagesStore from '../../stores/messagesStore'

import Messages from './Messages/Messages'
import TextForm from './TextForm'
import Loader from '../UI/Loader/Loader'
import TypingInfo from './TypingInfo'
import ChatHeader from './ChatHeader'
import ChatMembersModal from '../Modals/ChatMembersModal/ChatMembersModal'
import chatMembersModalStore from '../../stores/modals/chatMembersModalStore'


function SimpleChat() {
  const {sendStartTyping, sendStopTyping, sendText} = useSocket()

  const {loading, selectedChatId, isLoadMessages, loadError} = messagesStore
  const {login} = authStore.user

  const sendTextMessage = (text) => {
   sendText(text, selectedChatId)
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
        </div>
      </div>
      <div className="mt-2">
        <TypingInfo logins={messagesStore.selectedChatTypingLogins()}/>
      </div>
      <TextForm
        sendTextMessage={sendTextMessage}
        sendStartTyping={() => sendStartTyping(selectedChatId)}
        sendStopTyping={() => sendStopTyping(selectedChatId)}
      />
      <Modal show={addContactModalStore.show} onHide={closeAddContactModal}>
        <AddContactModal />
      </Modal>
      <Modal show={changeChatNameModalStore.show} onHide={() => changeChatNameModalStore.close()}>
        <ChangeChatNameModal />
      </Modal>
      <Modal show={chatMembersModalStore.show} onHide={() => chatMembersModalStore.close()}>
        <ChatMembersModal />
      </Modal>
    </div>
  )
}

export default observer(SimpleChat)