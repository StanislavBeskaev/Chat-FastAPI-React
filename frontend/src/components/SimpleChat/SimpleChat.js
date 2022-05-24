import React, {useEffect, useState} from 'react'

import authStore from '../../stores/authStore'
import {useSocket} from '../../contexts/SocketProvider'
import Messages from './Messages'
import TextForm from './TextForm'


function SimpleChat() {
  const [messages, setMessages] = useState([])

  const socket = useSocket()

  useEffect(() => {
    if (socket == null) return

    socket.onmessage = async (e) => {
      const msg = JSON.parse(e.data)
      console.log('Сообщение из ws: ', msg)
      addMessage(msg)
    }
  }, [socket])

  const addMessage = newMessage => {
    setMessages(prevMessages => [...prevMessages, newMessage])
  }

  const sendText = (text) => {
    console.log(`Отправка сообщения:`, text)
    socket.send(text)
  }

  return (
    <div className="d-flex flex-column flex-grow-1">
      <div className="flex-grow-1 overflow-auto">
        <div className="d-flex flex-column align-items-start justify-content-end px-3">
          <Messages messages={messages} login={authStore.user.login}/>
        </div>
      </div>
      <TextForm sendText={sendText}/>
    </div>
  )
}

export default SimpleChat