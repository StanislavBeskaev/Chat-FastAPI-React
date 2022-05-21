import React, {useEffect, useState} from 'react'
import {Button} from 'react-bootstrap'

import {useSocket} from '../../contexts/SocketProvider'

function SimpleChat() {
  const [message, setMessage] = useState('')
  const socket = useSocket()

  const sendMessage = () => {
    console.log(`Отправка сообщения:`, message)
    socket.send(message)
    setMessage('')
  }

  useEffect(() => {
    if (socket == null) return

    socket.onmessage = (e) => {
      const msg = JSON.parse(e.data)
      console.log("Сообщение из ws: ", msg)
    }
  }, [socket])

  return (
    <div className="d-flex flex-column">
      <h1>Тут будет чат</h1>
      <input
        value={message}
        onChange={e => setMessage(e.target.value)}
      />
      <Button onClick={sendMessage}>Отправить</Button>
    </div>

  )
}

export default SimpleChat