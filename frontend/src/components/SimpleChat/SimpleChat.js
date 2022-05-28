import React, {useEffect} from 'react'
import {observer} from 'mobx-react-lite'

import authStore from '../../stores/authStore'
import messagesStore from '../../stores/messagesStore'
import {useSocket} from '../../contexts/SocketProvider'
import Messages from './Messages'
import TextForm from './TextForm'



function SimpleChat() {
  const socket = useSocket()

  useEffect(() => {
    messagesStore.loadMessages()
      .then(() => {})
      .catch(e => console.log("Не удалось загрузить сообщения:", e))
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
    socket.send(text)
  }

  return (
    <div className="d-flex flex-column flex-grow-1">
      <div className="flex-grow-1 overflow-auto">
        <div className="d-flex flex-column align-items-start justify-content-end px-3">
          <Messages messages={messagesStore.messages} login={authStore.user.login}/>
        </div>
      </div>
      <TextForm sendText={sendText}/>
    </div>
  )
}

export default observer(SimpleChat)