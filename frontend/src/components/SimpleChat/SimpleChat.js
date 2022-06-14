import React from 'react'
import {observer} from 'mobx-react-lite'
import {Modal} from 'react-bootstrap'

import {useSocket} from '../../contexts/SocketProvider'

import authStore from '../../stores/authStore'
import messagesStore from '../../stores/messagesStore'
import addContactModalStore from '../../stores/modals/addContactModalStore'

import Messages from './Messages'
import TextForm from './TextForm'
import Loader from '../UI/Loader/Loader'
import AddContactModal from '../Modals/AddContactModal'


function SimpleChat() {
  const socket = useSocket()

  const {loading, selectedChatId, isLoadMessages, loadError} = messagesStore
  const {login} = authStore.user

  const sendText = (text) => {
    console.log(`Отправка сообщения:`, text)
    const textMessage = JSON.stringify(
      {
        type: "TEXT",
        data: {text, chatId: selectedChatId}
      }
    )
    socket.send(textMessage)
  }

  const sendTypingStart = () => {
    // TODO использовать debounce, посылать одно сообщение при старте и при окончании
    const typingStartMessage = JSON.stringify(
      {
        type: "START_TYPING",
        data: {chatId: selectedChatId}
      }
    )

    socket.send(typingStartMessage)
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
    <div className="d-flex flex-column flex-grow-1">
      <div className="flex-grow-1 overflow-auto">
        <div className="d-flex flex-column align-items-start justify-content-end px-3">
          <Messages messages={messagesStore.selectedChatMessages()} login={login}/>
        </div>
      </div>
      <TextForm sendText={sendText} sendTypingStart={sendTypingStart}/>
      <Modal show={addContactModalStore.show} onHide={closeAddContactModal}>
        <AddContactModal />
      </Modal>
    </div>
  )
}

export default observer(SimpleChat)