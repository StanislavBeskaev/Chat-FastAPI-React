import React, {useEffect, useState} from 'react'
import {observer} from 'mobx-react-lite'
import {Modal} from 'react-bootstrap'

import authStore from '../../stores/authStore'
import messagesStore from '../../stores/messagesStore'
import modalsStore from '../../stores/modalsStore'
import {useSocket} from '../../contexts/SocketProvider'
import Messages from './Messages'
import TextForm from './TextForm'
import Loader from '../UI/Loader/Loader'
import AddContactModal from '../Modals/AddContactModal'


function SimpleChat() {
  const [loading, setLoading] = useState(true)
  const socket = useSocket()

  const {messages, selectedChatId} = messagesStore
  const {login} = authStore.user


  useEffect(() => {
    messagesStore.loadMessages()
      .then(() => {})
      .catch(e => console.log("Не удалось загрузить сообщения:", e))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (socket == null) return

    socket.onmessage = async (e) => {
      const msg = JSON.parse(e.data)
      console.log('Сообщение из ws: ', msg)
      messagesStore.addMessage(msg)
    }
  }, [socket])


  const sendText = (text) => {
    console.log(`Отправка сообщения:`, text)
    const message = JSON.stringify({text, chatId: selectedChatId})
    socket.send(message)
  }

  const closeAddContactModal = () => {
    modalsStore.setShowAddContact(false)
    modalsStore.setAddContactLogin(null)
  }

  if (loading) {
    return <Loader />
  }

  return (
    <div className="d-flex flex-column flex-grow-1">
      <div className="flex-grow-1 overflow-auto">
        <div className="d-flex flex-column align-items-start justify-content-end px-3">
          <Messages messages={messages[selectedChatId]} login={login}/>
        </div>
      </div>
      <TextForm sendText={sendText}/>
      <Modal show={modalsStore.showAddContact} onHide={closeAddContactModal}>
        <AddContactModal />
      </Modal>
    </div>
  )
}

export default observer(SimpleChat)