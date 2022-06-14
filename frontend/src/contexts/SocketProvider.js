import React, { useContext, useEffect, useState } from 'react'

import {toast} from 'react-toastify'
import messagesStore from '../stores/messagesStore'


const SocketContext = React.createContext()

export function useSocket() {
  return useContext(SocketContext)
}

export function SocketProvider({ login, children }) {
  const [socket, setSocket] = useState()

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${login}`)
    setSocket(ws)

    ws.onmessage = async (e) => {
      const msg = JSON.parse(e.data)
      console.log('Сообщение из ws: ', msg)
      // TODO какие ещё нужны типы?
      switch (msg.type) {
        case 'TEXT':
          messagesStore.addMessage(msg.data)
          break
        case 'STATUS':
          addStatusNotification(msg.data)
          break
        case 'START_TYPING':
          messagesStore.addTypingLogin(msg.data.chat_id, msg.data.login)
          break
        case 'STOP_TYPING':
          messagesStore.deleteTypingLogin(msg.data.chat_id, msg.data.login)
          break
      }
    }

    return () => ws.close()
  }, [login])

  const addStatusNotification = data => {
    const {login: msgLogin, text, online_status: onlineStatus} = data

    if (login === msgLogin) return

    if (onlineStatus === "ONLINE") {
      toast.success(text)
    } else {
      toast.error(text)
    }
  }

  return (
    <SocketContext.Provider value={socket}>
      {children}
    </SocketContext.Provider>
  )
}